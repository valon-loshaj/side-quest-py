"""Database utility functions for the application."""

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Optional

# Add parent directory to path to make imports work
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Import the database setup
from src.side_quest_py.database import Base, engine, SessionLocal
from src.side_quest_py.api.config import settings


def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    logging.info("Database initialized: %s", settings.DATABASE_URL)


def reset_db() -> None:
    """Reset the database by dropping and recreating all tables."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logging.info("Database reset: %s", settings.DATABASE_URL)


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


def _seed_entity(session, entity_name: str, entities: List[Any]) -> None:
    """Add entities to the database and commit the transaction.

    Args:
        session: SQLAlchemy session
        entity_name: Name of the entity type for logging
        entities: List of entity instances to add
    """
    for entity in entities:
        session.add(entity)
    session.commit()
    logging.info("Added %d %s", len(entities), entity_name)


def seed_db() -> None:
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        from src.side_quest_py.models.db_models import User

        # Check if we already have users
        if db.query(User).count() > 0:
            logging.info("Database already contains data - skipping seed")
            return

        logging.info("Seeding database with initial data...")

        # Load seed data module
        seed_data_module = _load_seed_data_module()

        # Get the seed data
        seed_data = seed_data_module.get_seed_data()

        # Add entities in order (users, adventurers, quests, completions)
        _seed_entity(db, "users", seed_data["users"])
        _seed_entity(db, "adventurers", seed_data["adventurers"])
        _seed_entity(db, "quests", seed_data["quests"])
        _seed_entity(db, "quest_completions", seed_data["quest_completions"])

        logging.info("Database seeded successfully")

    except SQLAlchemyError as e:
        db.rollback()
        logging.error("Error seeding database: %s", e)
        raise
    except ImportError as e:
        logging.error("Error importing seed data module: %s", e)
        raise
    except Exception as e:
        db.rollback()
        logging.error("Unexpected error seeding database: %s", e)
        raise
    finally:
        db.close()


def get_db_status() -> dict:
    """Get the status of the database.

    Returns:
        dict: Database status information
    """
    db = SessionLocal()
    
    # Get environment info
    env = os.environ.get("FASTAPI_ENV", "development")
    uri = settings.DATABASE_URL

    try:
        db.execute(text("SELECT 1"))
        status = "connected"
    except SQLAlchemyError as e:
        status = f"error: {str(e)}"
    finally:
        db.close()

    return {"status": status, "uri": uri, "env": env}
