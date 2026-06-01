"""Telegram Bot initialization and dispatcher setup."""
import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.config import settings
from app.db.database import async_session

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    """Inject SQLAlchemy session into every handler."""
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


def create_bot() -> Bot:
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware(async_session))
    return dp


async def start_bot():
    """Start polling — called from main.py."""
    from app.bot.handlers import start, orders, wallet, services, admin

    bot = create_bot()
    dp = create_dispatcher()

    # Register routers (admin first for priority)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(orders.router)
    dp.include_router(wallet.router)
    dp.include_router(services.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started — polling...")
    await dp.start_polling(bot)
