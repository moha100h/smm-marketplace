"""Application configuration — loaded from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str = ""
    ADMIN_IDS: str = ""

    @property
    def admin_ids_list(self) -> list[int]:
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/sessionbot.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "change-me-to-a-random-string"
    JWT_EXPIRE_HOURS: int = 24
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Crypto
    USDT_TRC20_ADDRESS: str = ""
    USDT_BEP20_ADDRESS: str = ""
    BTC_ADDRESS: str = ""
    ETH_ADDRESS: str = ""
    LTC_ADDRESS: str = ""

    # Referral
    REFERRAL_COMMISSION_PERCENT: float = 10.0

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = False
    APP_DOMAIN: str = "localhost"

    # Backup
    BACKUP_INTERVAL_HOURS: int = 1
    BACKUP_RETAIN_DAYS: int = 7

    # Frontend
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
