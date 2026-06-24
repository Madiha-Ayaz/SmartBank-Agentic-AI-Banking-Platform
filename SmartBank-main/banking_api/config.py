from __future__ import annotations

import os
from pathlib import Path


class Settings:
    APP_NAME: str = "SmartFinance Dummy Banking API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    DB_PATH: str = os.getenv("BANKING_DB_PATH", str(ROOT_DIR / "banking_api" / "banking.db"))
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SIMULATE_EXTERNAL_APIS: bool = True


settings = Settings()
