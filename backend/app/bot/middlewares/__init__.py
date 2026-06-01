"""Middlewares — DB session, user auto-register, language injection."""
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.config import settings


class DatabaseMiddleware(BaseMiddleware):
    """Inject async DB session into handler data."""

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    """Load user from DB, auto-register, inject lang and is_admin."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # event IS the Message or CallbackQuery — not event.message
        if isinstance(event, Message):
            msg = event
        elif isinstance(event, CallbackQuery):
            msg = event.message
        else:
            return await handler(event, data)

        if not msg or not msg.from_user:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        tg_id = msg.from_user.id
        r = await session.execute(select(User).where(User.tg_id == tg_id))
        user = r.scalar_one_or_none()

        if not user:
            # Auto-register
            ref_code = None
            if isinstance(event, Message) and event.text and len(event.text.split()) > 1:
                ref_code = event.text.split()[1]

            import secrets
            user = User(
                tg_id=tg_id,
                username=msg.from_user.username,
                full_name=msg.from_user.full_name,
                referral_code=secrets.token_hex(6),
            )
            if ref_code:
                r2 = await session.execute(select(User).where(User.referral_code == ref_code))
                referrer = r2.scalar_one_or_none()
                if referrer:
                    user.referred_by_id = referrer.id

            session.add(user)
            await session.flush()

        data["user"] = user
        data["lang"] = user.language or "fa"
        data["is_admin"] = tg_id in settings.admin_ids_list

        return await handler(event, data)
