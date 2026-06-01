"""User-specific repository with wallet & referral logic."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, code: str) -> Optional[User]:
        stmt = select(User).where(User.referral_code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_to_wallet(self, user_id: int, amount: int) -> User:
        user = await self.session.get(User, user_id)
        if user:
            user.wallet_balance += amount
            await self.session.flush()
            await self.session.refresh(user)
        return user

    async def deduct_from_wallet(self, user_id: int, amount: int) -> bool:
        user = await self.session.get(User, user_id)
        if user and user.wallet_balance >= amount:
            user.wallet_balance -= amount
            await self.session.flush()
            return True
        return False
