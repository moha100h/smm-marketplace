"""Database engine and session factory."""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
