"""Order service — creation, status updates, partial completion engine."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderStatus, ProviderOrder
from app.models.user import User
from app.models.provider import Provider, ServiceProviderMapping
from app.services.wallet_service import WalletService
from app.adapters.provider_router import provider_router
from app.repositories.order_repo import OrderRepository
import logging

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.wallet_service = WalletService(session)

    async def create_order(
        self,
        user_id: int,
        service_id: int,
        quantity: int,
        price_per_1000: int,
        form_data: str,
    ) -> Order:
        """Create order, deduct wallet, route to provider."""
        total_cost = (quantity * price_per_1000) // 1000

        # Deduct from wallet
        await self.wallet_service.process_purchase(user_id, total_cost, order_id=0)  # temp 0, update later

        # Create order
        order = Order(
            user_id=user_id,
            service_id=service_id,
            quantity=quantity,
            price_per_1000=price_per_1000,
            total_cost=total_cost,
            paid_amount=total_cost,
            form_data=form_data,
            status=OrderStatus.PENDING,
        )
        self.session.add(order)
        await self.session.flush()

        # Route to provider
        # (In production, fetch mappings & providers from DB)
        # result = await provider_router.route_order(...)

        return order

    async def update_order_status(self, order_id: int, status: OrderStatus) -> Order:
        """Update order status."""
        order = await self.order_repo.get_by_id(order_id)
        if order:
            order.status = status
            await self.session.flush()
        return order

    async def process_partial_completion(
        self,
        order_id: int,
        delivered_quantity: int,
    ) -> Order:
        """Handle partial delivery — calculate refund for undelivered portion."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        order.charged_quantity = delivered_quantity
        remaining = order.quantity - delivered_quantity

        if remaining > 0:
            # Calculate refund for undelivered portion
            refund_amount = (remaining * order.price_per_1000) // 1000
            order.refunded_amount += refund_amount
            order.status = OrderStatus.PARTIALLY_COMPLETED

            # Process refund
            await self.wallet_service.process_refund(
                user_id=order.user_id,
                amount=refund_amount,
                order_id=order_id,
                reason=f"Partial completion refund ({remaining} units)",
            )
        else:
            order.status = OrderStatus.COMPLETED
            order.completed_at = order.updated_at

        await self.session.flush()
        return order
