"""
Centralized configuration for the Side Quest FastAPI application.

This module handles loading environment variables and provides configuration
settings for different environments (development, testing, production).
"""

import os
import sys
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


FASTAPI_ENV = os.environ.get("FASTAPI_ENV")
if not FASTAPI_ENV:
    raise ValueError("FASTAPI_ENV is not set")
print(f"Using environment: {FASTAPI_ENV}", file=sys.stderr)


class BaseConfig(BaseSettings):
    """Base configuration for all environments."""

    # API settings
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"

    # Application settings
    APP_NAME: str = "Side Quest API"
    APP_DESCRIPTION: str = "A Python adventure quest tracking API"
    APP_VERSION: str = "0.1.0"

    # Security settings
    SECRET_KEY: str | None = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database settings
    DATABASE_URL: str | None = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")

    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Pydantic v2 config using model_config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG: bool = True


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING: bool = True


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG: bool = False

    # In production, we enforce having a strong secret key
    @property
    def SECRET_KEY(self) -> str:
        """Get the secret key from environment variables."""
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            raise ValueError("Production environment must set SECRET_KEY environment variable")
        return secret_key

    # Override CORS settings for production
    CORS_ORIGINS: list = ["https://yourdomain.com", "https://api.yourdomain.com"]


# Configuration dictionary
config_dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


@lru_cache()
def get_settings():
    """
    Get application settings based on environment.
    Uses lru_cache to avoid loading the settings multiple times.
    """
    env = os.environ.get("FASTAPI_ENV", "development")
    config_class = config_dict.get(env, DevelopmentConfig)
    return config_class()


# Create a settings instance for import
settings = get_settings()
