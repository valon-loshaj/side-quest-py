"""Database initialization script.

This script initializes the database and creates all tables.
"""

import os
import sys
import sqlite3

import click
from flask import Flask
from flask.cli import with_appcontext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def init_database() -> None:
    """Initialize the database with all tables.

    This uses the DATABASE_URL from environment variables.
    """
    # Get the environment from environment variable, default to development
    env = os.environ.get("FLASK_ENV", "development")
    print(f"Environment: {env}")

    # Get database URL from environment, or use a default as fallback
    database_url = os.environ.get("DATABASE_URL")
    print(f"DATABASE_URL: {database_url}")
    if not database_url:
        raise ValueError("DATABASE_URL is not set")
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

    # Remove if exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database at {db_path}")
        except Exception as e:
            print(f"Warning: Could not remove existing database: {e}")

    # First test direct SQLite access
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_access (id INTEGER PRIMARY KEY)")
        cursor.close()
        conn.close()
        print("✅ Direct SQLite access works")
        os.remove(db_path)  # Remove test table for clean slate
    except Exception as e:
        print(f"❌ Direct SQLite test failed: {e}")
        sys.exit(1)

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
            db.create_all()
            print("\n✅ Database initialized successfully")

            # List all tables created
            from sqlalchemy import inspect

            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables created: {tables}")

            # Print database location for reference
            print(f"\nDatabase created at: {db_path}")
            print(f"You can set this in your .env file with:")
            print(f"DATABASE_URL=sqlite:///{db_path}")

        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """Flask CLI command to initialize the database."""
    click.echo("Initializing the database...")
    init_database()
    click.echo("Database initialized!")


if __name__ == "__main__":
    print("Starting database initialization...")
    init_database()
