"""Database initialization script.

This script initializes the database and creates all tables.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to make imports work
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent.parent
sys.path.insert(0, str(root_dir))

import click
from dotenv import load_dotenv
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

# Import database and settings
from src.side_quest_py.database import Base, engine, SessionLocal
from src.side_quest_py.api.config import settings


def init_database() -> None:
    """Initialize the database with all tables.

    This uses the DATABASE_URL from environment variables.
    """
    # Get the environment from environment variable, default to development
    env = os.environ.get("FASTAPI_ENV", "development")
    print(f"Environment: {env}")

    # Get database URL from environment
    database_url = settings.DATABASE_URL
    print(f"Using DATABASE_URL: {database_url}")

    # Import models to ensure they're registered with SQLAlchemy
    from src.side_quest_py.models.db_models import Adventurer, Quest, QuestCompletion, User

    try:
        # Test database connection first
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            print("✅ Database connection successful")

        # Now create all tables
        Base.metadata.create_all(engine)
        print("\n✅ Database initialized successfully")

        # List all tables created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables created: {tables}")

    except SQLAlchemyError as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def init_db_command() -> None:
    """Flask CLI command to initialize the database."""
    click.echo("Initializing the database...")
    init_database()
    click.echo("Database initialized!")


if __name__ == "__main__":
    print("Starting database initialization...")
    init_database()
