import os
from typing import Any, Dict, Optional


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default database path is in backend instance folder
    # Get the absolute path to the backend package directly
    _BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    _INSTANCE_PATH = os.path.join(_BACKEND_PATH, "instance")

    # Ensure instance directory exists
    os.makedirs(_INSTANCE_PATH, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    # Use explicit absolute path to avoid any confusion
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(Config._INSTANCE_PATH, 'side_quest_dev.db')}"
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    # Use explicit absolute path to avoid any confusion
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", f"sqlite:///{os.path.join(Config._INSTANCE_PATH, 'side_quest_test.db')}"
    )

    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    # Use explicit absolute path to avoid any confusion
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
