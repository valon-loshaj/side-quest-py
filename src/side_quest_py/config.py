import os
from typing import Any, Dict, Optional


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default database path is in instance folder
    _INSTANCE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "instance"))


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(Config._INSTANCE_PATH, 'side_quest_dev.db')}"
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    # Use in-memory database for testing by default
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", f"sqlite:///{os.path.join(Config._INSTANCE_PATH, 'side_quest_test.db')}"
    )

    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    # Production database can be set via environment variable
    # Default to SQLite but consider PostgreSQL or MySQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(Config._INSTANCE_PATH, 'side_quest.db')}"
    )

    # Production should use a strong secret key
    SECRET_KEY = os.environ.get("SECRET_KEY")  # type: ignore
    if not SECRET_KEY:  # type: ignore
        raise ValueError("Production environment must set SECRET_KEY environment variable")


config: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
