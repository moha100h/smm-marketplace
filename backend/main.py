"""Application entry point."""
import asyncio
import logging
from app.core.config import settings
from app.db.database import engine
from app.db.base import Base
from app.bot.bot import start_bot

# Import all models so tables are created
import app.models  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized — tables created")


async def main():
    await init_db()
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
