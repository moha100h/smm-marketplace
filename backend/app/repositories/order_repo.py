"""Order repository with status tracking."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderStatus
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: OrderStatus, limit: int = 50) -> List[Order]:
        stmt = select(Order).where(Order.status == status).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
