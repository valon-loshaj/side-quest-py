"""Configuration for the Side Quest application.

Raises:
    ValueError: If the DATABASE_URL is not set.
"""

import os
from typing import Any, Dict


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default database path is in backend instance folder
    # Get the absolute path to the backend package directly
    _BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    INSTANCE_PATH = os.path.join(_BACKEND_PATH, "instance")

    # Ensure instance directory exists
    os.makedirs(INSTANCE_PATH, exist_ok=True)

    # Check if user home directory is used for database
    HOME_DB_PATH = os.path.join(os.path.expanduser("~"), ".side_quest_py")
    # Ensure home db directory exists if DATABASE_URL points there
    if os.environ.get("DATABASE_URL") and ".side_quest_py" in os.environ.get("DATABASE_URL", ""):
        os.makedirs(HOME_DB_PATH, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_dev"
    )
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL is not set")


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_test"
    )

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL is not set")

    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://side_quest_admin:your_secure_password@localhost/side_quest_prod"
    )

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL is not set")

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

INSTANCE_PATH = Config.INSTANCE_PATH
