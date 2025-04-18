"""Database reset script.

This script drops all tables and recreates them, effectively resetting the database.
"""

import os
import sys
import sqlite3
from pathlib import Path

import click
from flask import Flask
from flask.cli import with_appcontext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# We'll import models later after setting up Flask app


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables.

    This uses the DATABASE_URL from environment variables.
    """
    # Get the environment from environment variable, default to development
    env = os.environ.get("FLASK_ENV", "development")
    print(f"Environment: {env}")

    # Get database URL from environment, or use a default as fallback
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        # Use instance directory in the project
        from src.side_quest_py.config import INSTANCE_PATH

        db_path = os.path.join(INSTANCE_PATH, f"side_quest_{env}.db")
        database_url = f"sqlite:///{db_path}"
        print(f"No DATABASE_URL found in environment. Using default: {database_url}")
    else:
        print(f"Using DATABASE_URL from environment: {database_url}")

    # Extract the file path from the SQLite URL
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"Database path: {db_path}")
    else:
        print(f"Warning: Non-SQLite database URL detected: {database_url}")
        print("This script is designed for SQLite databases.")
        sys.exit(1)

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

    # Use a clean Flask app with direct configuration
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Import database and models
    from src.side_quest_py import db

    # Import models to ensure they're registered with SQLAlchemy
    from src.side_quest_py.models import Adventurer, Quest, QuestCompletion, User

    # Initialize the database with our app
    db.init_app(app)

    with app.app_context():
        try:
            # Drop all tables first
            db.drop_all()
            print("Dropped all existing tables")

            # Then recreate them
            db.create_all()
            print("\n✅ Database reset successfully")

            # List all tables created
            from sqlalchemy import inspect

            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables recreated: {tables}")

            # Print database location for reference
            print(f"\nDatabase reset at: {db_path}")
            print(f"You can set this in your .env file with:")
            print(f"DATABASE_URL=sqlite:///{db_path}")

        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            sys.exit(1)


@click.command("reset-db")
@with_appcontext
def reset_db_command() -> None:
    """Flask CLI command to reset the database."""
    click.echo("Resetting the database...")
    reset_database()
    click.echo("Database reset successfully!")


if __name__ == "__main__":
    print("Starting database reset...")
    reset_database()
