"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Application
    APP_NAME: str = "DataInsight"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    ENVIRONMENT: str = "development"

    # Database - defaults to SQLite for local dev without MySQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # Redis - optional for MVP, set to empty string to disable
    REDIS_URL: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
