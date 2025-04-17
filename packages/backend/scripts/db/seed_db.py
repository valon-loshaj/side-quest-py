"""Database seed script.

This script seeds the database with initial data for development and testing.
"""

import logging
import os
from typing import Optional

import click
from flask import Flask
from flask.cli import with_appcontext
from sqlalchemy.exc import SQLAlchemyError

from src.side_quest_py import create_app, db
from src.side_quest_py.config import config
from src.side_quest_py.models.db_models import User

# Import the seed data helper
from scripts.db.seed_data import get_seed_data


def _seed_entity(entity_name: str, entities) -> None:
    """Add entities to the database and commit the transaction.

    Args:
        entity_name: Name of the entity type for logging
        entities: List of entity instances to add
    """
    for entity in entities:
        db.session.add(entity)
    db.session.commit()
    logging.info("Added %d %s", len(entities), entity_name)


def seed_database(app: Optional[Flask] = None) -> None:
    """Seed the database with initial data.

    Args:
        app: Flask application instance (optional)
    """
    # Get the environment from environment variable, default to development
    env = os.environ.get("FLASK_ENV", "development")

    if app is None:
        app = create_app()
        app.config.from_object(config[env])

    # Ensure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Fix the database path to be within the backend instance folder
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    instance_path = os.path.join(backend_path, "instance")
    db_file = (
        "side_quest_dev.db" if env == "development" else ("side_quest_test.db" if env == "testing" else "side_quest.db")
    )
    db_path = os.path.join(instance_path, db_file)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    logging.info(f"Using database path: {db_path}")

    with app.app_context():
        try:
            # Check if we already have users
            if User.query.count() > 0:
                logging.info("Database already contains data - skipping seed")
                return

            logging.info("Seeding database with initial data...")

            # Get the seed data
            seed_data = get_seed_data()

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
        except Exception as e:
            db.session.rollback()
            logging.error("Unexpected error seeding database: %s", e)
            raise


@click.command("seed-db")
@with_appcontext
def seed_db_command() -> None:
    """Flask CLI command to seed the database."""
    click.echo("Seeding the database...")
    seed_database()
    click.echo("Database seeded successfully!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Run directly if script is executed
    env = os.environ.get("FLASK_ENV", "development")
    app = create_app()
    app.config.from_object(config[env])

    with app.app_context():
        seed_database(app)
