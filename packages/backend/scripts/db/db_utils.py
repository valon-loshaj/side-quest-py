"""Database utility functions for the application."""

import importlib.util
import logging
import os
import sys
from typing import Any, List, Optional

from flask import Flask, current_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Import the SQLAlchemy instance directly
from src.side_quest_py import db


def init_db(app: Optional[Flask] = None) -> None:
    """Initialize the database by creating all tables.

    Args:
        app: Flask application instance (optional)
    """
    # Get the app if not provided
    if app is None:
        app = current_app

    db.create_all()
    logging.info("Database initialized: %s", app.config["SQLALCHEMY_DATABASE_URI"])


def reset_db(app: Optional[Flask] = None) -> None:
    """Reset the database by dropping and recreating all tables.

    Args:
        app: Flask application instance (optional)
    """
    # Get the app if not provided
    if app is None:
        app = current_app

    db.drop_all()
    db.create_all()
    logging.info("Database reset: %s", app.config["SQLALCHEMY_DATABASE_URI"])


def _load_seed_data_module() -> Any:
    """Load the seed data module from the scripts/db directory."""
    # Find the absolute path to the seed_data.py module
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    scripts_path = os.path.join(project_root, "scripts", "db", "seed_data.py")

    logging.info("Looking for seed data module at: %s", scripts_path)

    spec = importlib.util.spec_from_file_location("seed_data", scripts_path)
    seed_data_module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules["seed_data"] = seed_data_module
    spec.loader.exec_module(seed_data_module)  # type: ignore

    return seed_data_module


def _seed_entity(entity_name: str, entities: List[Any]) -> None:
    """Add entities to the database and commit the transaction.

    Args:
        entity_name: Name of the entity type for logging
        entities: List of entity instances to add
    """
    for entity in entities:
        db.session.add(entity)
    db.session.commit()
    logging.info("Added %d %s", len(entities), entity_name)


def seed_db(app: Optional[Flask] = None) -> None:
    """Seed the database with initial data.

    Args:
        app: Flask application instance (optional)
    """
    # Get the app if not provided
    if app is None:
        app = current_app

    try:
        from src.side_quest_py.models.db_models import User

        # Check if we already have users
        if User.query.count() > 0:
            logging.info("Database already contains data - skipping seed")
            return

        logging.info("Seeding database with initial data...")

        # Load seed data module
        seed_data_module = _load_seed_data_module()

        # Get the seed data
        seed_data = seed_data_module.get_seed_data()

        # Add entities in order (users, adventurers, quests, completions)
        _seed_entity("users", seed_data["users"])
        _seed_entity("adventurers", seed_data["adventurers"])
        _seed_entity("quests", seed_data["quests"])
        _seed_entity("quest_completions", seed_data["quest_completions"])

        logging.info("Database seeded successfully")

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error("Error seeding database: %s", e)
        raise
    except ImportError as e:
        logging.error("Error importing seed data module: %s", e)
        raise
    except Exception as e:
        db.session.rollback()
        logging.error("Unexpected error seeding database: %s", e)
        raise


def get_db_status(app: Optional[Flask] = None) -> dict:
    """Get the status of the database.

    Args:
        app: Flask application instance (optional)

    Returns:
        dict: Database status information
    """
    # Get the app if not provided
    if app is None:
        app = current_app

    # Get database URI and environment info first in case db connection fails
    env = app.config.get("ENV") or app.config.get("FLASK_ENV", "development")
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "not_configured")
    track_modifications = app.config.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    try:
        db.session.execute(text("SELECT 1"))
        status = "connected"
    except SQLAlchemyError as e:
        status = f"error: {str(e)}"

    return {"status": status, "uri": uri, "track_modifications": track_modifications, "env": env}
