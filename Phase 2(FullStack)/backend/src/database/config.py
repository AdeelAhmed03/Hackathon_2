"""Database configuration settings."""

from pydantic_settings import Settings
from typing import Optional
import os

class Settings(Settings):
    """Database settings configuration."""

    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_app")
    db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

# Create settings instance
settings = Settings()