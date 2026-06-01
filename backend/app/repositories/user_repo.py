"""User repository."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        return await self.session.get(User, tg_id)

    async def get_by_referral_code(self, code: str) -> Optional[User]:
        stmt = select(User).where(User.referral_code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, tg_id: int, **kwargs) -> User:
        user = await self.get_by_tg_id(tg_id)
        if user:
            return user
        user = User(tg_id=tg_id, **kwargs)
        self.session.add(user)
        await self.session.flush()
        return user
