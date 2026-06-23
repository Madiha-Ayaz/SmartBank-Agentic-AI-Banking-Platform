from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "SmartBank API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./smartbank.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_ENABLED: bool = False

    JWT_SECRET_KEY: str = "smartbank-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CBS_API_BASE_URL: str = "https://cbs.smartbank.internal/api/v1"
    CBS_API_KEY: str = ""

    UI_PATH_ORCHESTRATOR_URL: str = ""
    UI_PATH_ORCHESTRATOR_TENANT: str = ""
    UI_PATH_ORCHESTRATOR_CLIENT_ID: str = ""
    UI_PATH_ORCHESTRATOR_CLIENT_SECRET: str = ""

    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    CORS_ORIGINS: list[str] = ["*"]

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"

    WS_HEARTBEAT_INTERVAL: int = 30

    ROOT_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent


settings = Settings()

LOG_LEVEL_MAP = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}
