"""Application configuration module."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "task-tracker-api")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    database_path: str = os.getenv("DATABASE_PATH", "tasks.db")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


settings = Settings()
