"""Order repository."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.order import Order, OrderStatus
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_user(self, user_id: int, limit: int = 50) -> List[Order]:
        stmt = select(Order).where(Order.user_id == user_id).order_by(desc(Order.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: OrderStatus, limit: int = 50) -> List[Order]:
        stmt = select(Order).where(Order.status == status).order_by(desc(Order.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_orders(self) -> List[Order]:
        return await self.get_by_status(OrderStatus.PENDING)
