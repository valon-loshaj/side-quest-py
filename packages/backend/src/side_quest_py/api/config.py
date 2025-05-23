"""
Centralized configuration for the Side Quest FastAPI application.

This module handles loading environment variables and provides configuration
settings for different environments (development, testing, production).
"""

import os
import sys
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# load environment variables
load_dotenv()

FASTAPI_ENV = os.environ.get("FASTAPI_ENV")
if not FASTAPI_ENV:
    raise ValueError("FASTAPI_ENV is not set")
print(f"Using environment: {FASTAPI_ENV}", file=sys.stderr)


class BaseConfig(BaseSettings):
    """Base configuration for all environments."""

    # Environment
    FASTAPI_ENV: str = FASTAPI_ENV

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

    # Debug flag
    DEBUG: bool = False

    # Gunicorn settings
    GUNICORN_BIND: str | None = os.environ.get("GUNICORN_BIND")
    if not GUNICORN_BIND:
        raise ValueError("GUNICORN_BIND is not set")
    GUNICORN_WORKERS: int | None = (
        int(os.environ.get("GUNICORN_WORKERS")) if os.environ.get("GUNICORN_WORKERS") else None  # type: ignore
    )
    if not GUNICORN_WORKERS:
        raise ValueError("GUNICORN_WORKERS is not set")
    GUNICORN_WORKER_CLASS: str | None = os.environ.get("GUNICORN_WORKER_CLASS")
    if not GUNICORN_WORKER_CLASS:
        raise ValueError("GUNICORN_WORKER_CLASS is not set")
    GUNICORN_ACCESS_LOG: str | None = os.environ.get("GUNICORN_ACCESS_LOG")
    if not GUNICORN_ACCESS_LOG:
        raise ValueError("GUNICORN_ACCESS_LOG is not set")
    GUNICORN_ERROR_LOG: str | None = os.environ.get("GUNICORN_ERROR_LOG")
    if not GUNICORN_ERROR_LOG:
        raise ValueError("GUNICORN_ERROR_LOG is not set")
    GUNICORN_LOG_LEVEL: str | None = os.environ.get("GUNICORN_LOG_LEVEL")
    if not GUNICORN_LOG_LEVEL:
        raise ValueError("GUNICORN_LOG_LEVEL is not set")
    GUNICORN_TIMEOUT: int | None = (
        int(os.environ.get("GUNICORN_TIMEOUT")) if os.environ.get("GUNICORN_TIMEOUT") else None  # type: ignore
    )
    if not GUNICORN_TIMEOUT:
        raise ValueError("GUNICORN_TIMEOUT is not set")
    GUNICORN_KEEPALIVE: int | None = (
        int(os.environ.get("GUNICORN_KEEPALIVE")) if os.environ.get("GUNICORN_KEEPALIVE") else None  # type: ignore
    )
    if not GUNICORN_KEEPALIVE:
        raise ValueError("GUNICORN_KEEPALIVE is not set")

    # Celery settings
    CELERY_BROKER_URL: str | None = os.environ.get("CELERY_BROKER_URL")
    if not CELERY_BROKER_URL:
        raise ValueError("CELERY_BROKER_URL is not set")

    # RabbitMQ settings
    RABBITMQ_URL: str | None = os.environ.get("RABBITMQ_URL")
    if not RABBITMQ_URL:
        raise ValueError("RABBITMQ_URL is not set")

    # SMTP settings
    SMTP_SERVER: str | None = os.environ.get("SMTP_SERVER")
    if not SMTP_SERVER:
        raise ValueError("SMTP_SERVER is not set")
    SMTP_PORT: int | None = int(os.environ.get("SMTP_PORT")) if os.environ.get("SMTP_PORT") else None  # type: ignore
    if not SMTP_PORT:
        raise ValueError("SMTP_PORT is not set")
    SMTP_USERNAME: str | None = os.environ.get("SMTP_USERNAME")
    if not SMTP_USERNAME:
        raise ValueError("SMTP_USERNAME is not set")
    SMTP_PASSWORD: str | None = os.environ.get("SMTP_PASSWORD")
    if not SMTP_PASSWORD:
        raise ValueError("SMTP_PASSWORD is not set")
    SMTP_SENDER_EMAIL: str | None = os.environ.get("SMTP_SENDER_EMAIL")
    if not SMTP_SENDER_EMAIL:
        raise ValueError("SMTP_SENDER_EMAIL is not set")

    # Pydantic v2 config using model_config
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


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
    cached_env = FASTAPI_ENV
    config_class = config_dict.get(cached_env if cached_env is not None else "development")
    if not config_class:
        raise ValueError(f"Invalid environment: {cached_env}")
    return config_class()


# Create a settings instance for import
settings = get_settings()
