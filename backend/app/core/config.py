"""Application settings from environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/sessionbot"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRE_HOURS: int = 24
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    USDT_TRC20_ADDRESS: str = ""
    USDT_BEP20_ADDRESS: str = ""
    BTC_ADDRESS: str = ""
    ETH_ADDRESS: str = ""
    LTC_ADDRESS: str = ""
    REFERRAL_COMMISSION_PERCENT: int = 10
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = False
    APP_DOMAIN: str = "localhost"
    BACKUP_INTERVAL_HOURS: int = 1
    BACKUP_RETAIN_DAYS: int = 7

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
