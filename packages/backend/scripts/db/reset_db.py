"""Database reset script.

This script drops all tables and recreates them, effectively resetting the database.
"""

import os
import sys
import sqlite3
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
from src.side_quest_py.database import Base, engine
from src.side_quest_py.api.config import settings


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables.

    This uses the DATABASE_URL from environment variables.
    """
    # Get the environment from environment variable, default to development
    env = os.environ.get("FASTAPI_ENV", "development")
    print(f"Environment: {env}")

    # Get database URL from environment
    database_url = settings.DATABASE_URL
    print(f"Using DATABASE_URL: {database_url}")

    # Extract the file path from the SQLite URL if it's SQLite
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"Database path: {db_path}")

        # Verify database exists
        if not os.path.exists(db_path):
            print(f"Warning: Database file does not exist at {db_path}")
            print("Will create a new database instead.")
        else:
            print(f"Found existing database at {db_path}")

        # First test direct SQLite access
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Just check if we can access the database
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            print("✅ Direct SQLite access works")
        except Exception as e:
            print(f"❌ Direct SQLite test failed: {e}")
            print("Continuing anyway, will create a new database file...")
    else:
        print(f"Using non-SQLite database: {database_url}")

    # Import models to ensure they're registered with SQLAlchemy
    from src.side_quest_py.models.db_models import Adventurer, Quest, QuestCompletion, User

    try:
        # Drop all tables first
        Base.metadata.drop_all(engine)
        print("Dropped all existing tables")

        # Then recreate them
        Base.metadata.create_all(engine)
        print("\n✅ Database reset successfully")

        # List all tables created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables recreated: {tables}")

        # Print database location for reference if SQLite
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            print(f"\nDatabase reset at: {db_path}")
            print(f"You can set this in your .env file with:")
            print(f"DATABASE_URL=sqlite:///{db_path}")

    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Starting database reset...")
    reset_database()
