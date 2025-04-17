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

# We'll import models later after setting up Flask app


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables.

    This uses a custom approach to bypass configuration issues.
    """
    # Get the environment from environment variable, default to development
    env = os.environ.get("FLASK_ENV", "development")
    print(f"Environment: {env}")

    # Use ~/.side_quest_py directory for database
    home_dir = str(Path.home())
    db_dir = os.path.join(home_dir, ".side_quest_py")
    os.makedirs(db_dir, exist_ok=True)
    print(f"Database directory: {db_dir}")

    # Create database file path
    db_file = f"side_quest_{env}.db"
    db_path = os.path.join(db_dir, db_file)
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

    # Use a clean Flask app with direct configuration
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
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
