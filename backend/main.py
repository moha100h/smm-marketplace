"""Application entry point — starts FastAPI + Telegram Bot."""
import asyncio
import logging
from app.core.config import settings
from app.db.database import engine, async_session
from app.db.base import Base
from app.bot.bot import start_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def main():
    await init_db()

    # Start scheduler in background
    from app.tasks.scheduler import start_scheduler
    from app.bot.bot import create_bot

    bot = create_bot()
    asyncio.create_task(start_scheduler(bot, async_session))

    # Start bot polling
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
