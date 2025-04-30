"""Database seed script.

This script seeds the database with initial data for development and testing.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to make imports work
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent.parent
sys.path.insert(0, str(root_dir))

import click
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.side_quest_py.models.db_models import User
from src.side_quest_py.database import SessionLocal, engine
from src.side_quest_py.api.config import settings

# Import the seed data helper
from scripts.db.seed_data import get_seed_data


def _seed_entity(session, entity_name: str, entities) -> None:
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


def seed_database() -> None:
    """Seed the database with initial data."""
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if we already have users
        if db.query(User).count() > 0:
            logging.info("Database already contains data - skipping seed")
            return

        logging.info("Seeding database with initial data...")

        # Get the seed data
        seed_data = get_seed_data()

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
    except Exception as e:
        db.rollback()
        logging.error("Unexpected error seeding database: %s", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Log environment info
    logging.info(f"Environment: {os.environ.get('FASTAPI_ENV', 'development')}")
    logging.info(f"Database URL: {settings.DATABASE_URL}")
    
    # Run database seeding
    seed_database()
    logging.info("Database seeded successfully!")
