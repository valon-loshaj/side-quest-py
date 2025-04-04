from typing import Dict, Any
import os


class Config:
    """Base configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///side_quest_dev.db"
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///side_quest_test.db"
    )


class ProductionConfig(Config):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///side_quest.db")
    SECRET_KEY = os.environ.get("SECRET_KEY")


config: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
