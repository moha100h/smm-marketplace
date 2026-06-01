"""Order service — creation, status updates, partial completion engine."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderStatus, ProviderOrder
from app.models.user import User
from app.models.provider import Provider, ServiceProviderMapping
from app.services.wallet_service import WalletService
from app.adapters.provider_router import ProviderRouter
from app.repositories.order_repo import OrderRepository
import logging

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.wallet_service = WalletService(session)
        self.provider_router = ProviderRouter(session)

    async def _get_user(self, user_id: int):
        """Get user by tg_id."""
        r = await self.session.execute(select(User).where(User.tg_id == user_id))
        return r.scalar_one_or_none()

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

        # Step 1: Deduct from wallet FIRST
        user = await self._get_user(user_id)
        if not user:
            raise ValueError("User not found")
        if user.wallet_balance < total_cost:
            raise ValueError("Insufficient wallet balance")

        balance_before = user.wallet_balance
        user.wallet_balance -= total_cost
        await self.session.flush()

        # Step 2: Create order
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

        # Step 3: Record transaction
        from app.models.payment import Transaction, TransactionType
        tx = Transaction(
            user_id=user_id,
            order_id=order.id,
            type=TransactionType.PURCHASE,
            amount=-total_cost,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description=f"Order #{order.id} purchase",
        )
        self.session.add(tx)
        await self.session.flush()

        # Step 4: Update user stats
        user.total_spent += total_cost
        user.total_orders += 1
        user.update_loyalty()

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
            refund_amount = (remaining * order.price_per_1000) // 1000
            order.refunded_amount += refund_amount
            order.status = OrderStatus.PARTIALLY_COMPLETED

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
