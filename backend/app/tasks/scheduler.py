"""Background tasks — provider health, order status sync, backups."""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from aiogram import Bot
from app.models.provider import Provider, ProviderStatus
from app.models.order import Order, OrderStatus, ProviderOrder
from app.adapters.smm_api import SMMApiAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)

HEALTH_CHECK_INTERVAL = 300  # 5 minutes
ORDER_SYNC_INTERVAL = 60     # 1 minute


async def check_provider_health(session_factory: async_sessionmaker):
    """Check all active providers and update health status."""
    async with session_factory() as session:
        r = await session.execute(select(Provider).where(Provider.status == ProviderStatus.ACTIVE))
        providers = r.scalars().all()

        for provider in providers:
            try:
                adapter = SMMApiAdapter(provider.api_url, provider.api_key)
                import time
                start = time.time()
                balance = await adapter.get_balance()
                elapsed = (time.time() - start) * 1000

                provider.response_time_ms = elapsed
                provider.last_checked_at = datetime.utcnow()
                provider.health_status = "ok" if elapsed < 3000 else "slow"
                provider.success_rate = min(100, provider.success_rate + 0.1)

                if elapsed > 10000:
                    provider.health_status = "unhealthy"
                    provider.status = ProviderStatus.UNHEALTHY
                    logger.warning(f"Provider {provider.name} unhealthy: {elapsed:.0f}ms")

            except Exception as e:
                provider.error_rate = min(100, provider.error_rate + 1)
                provider.success_rate = max(0, provider.success_rate - 1)
                provider.health_status = "error"
                logger.error(f"Provider {provider.name} check failed: {e}")

        await session.commit()


async def sync_order_statuses(session_factory: async_sessionmaker, bot: Bot):
    """Sync pending/processing orders with providers."""
    async with session_factory() as session:
        r = await session.execute(
            select(Order).where(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING])
            ).limit(50)
        )
        orders = r.scalars().all()

        for order in orders:
            # Get provider orders for this order (direct query, not relationship)
            pr = await session.execute(
                select(ProviderOrder).where(
                    ProviderOrder.order_id == order.id,
                    ProviderOrder.provider_order_ref.isnot(None)
                )
            )
            prov_orders = pr.scalars().all()

            for po in prov_orders:
                try:
                    adapter = SMMApiAdapter(
                        po.provider.api_url,
                        po.provider.api_key,
                    )
                    status = await adapter.get_order_status(po.provider_order_ref)

                    charge = status.get("charge") or status.get("remains")
                    if charge is not None:
                        delivered = order.quantity - int(charge)
                        if delivered >= order.quantity:
                            order.status = OrderStatus.COMPLETED
                            order.charged_quantity = order.quantity
                        elif delivered > 0:
                            order.status = OrderStatus.PARTIALLY_COMPLETED
                            order.charged_quantity = delivered

                except Exception as e:
                    logger.error(f"Order {order.id} sync failed: {e}")

        await session.commit()


async def start_scheduler(bot: Bot, session_factory: async_sessionmaker):
    """Start background tasks."""
    logger.info("Scheduler started")

    while True:
        try:
            await check_provider_health(session_factory)
            await sync_order_statuses(session_factory, bot)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        await asyncio.sleep(ORDER_SYNC_INTERVAL)
