"""Bot setup — create, configure, start."""
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.core.config import settings
from app.db.database import async_session
from app.bot.middlewares import DatabaseMiddleware, UserMiddleware

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    return Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dp() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares
    dp.update.middleware(DatabaseMiddleware(async_session))
    dp.update.middleware(UserMiddleware())

    # Register routers
    from app.bot.handlers.start import router as start_router
    from app.bot.handlers.wallet import router as wallet_router
    from app.bot.handlers.orders import router as orders_router
    from app.bot.handlers.admin import router as admin_router
    from app.bot.handlers.settings import router as settings_router
    from app.bot.handlers.support import router as support_router

    dp.include_router(start_router)
    dp.include_router(wallet_router)
    dp.include_router(orders_router)
    dp.include_router(admin_router)
    dp.include_router(settings_router)
    dp.include_router(support_router)

    return dp


async def start_bot():
    bot = create_bot()
    dp = create_dp()
    logger.info("Bot started — polling...")
    await dp.start_polling(bot)
