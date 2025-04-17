"""Database initialization script.

This script initializes the database and creates all tables.
"""

import os
import sys
import sqlite3
from pathlib import Path

import click
from flask import Flask
from flask.cli import with_appcontext

# We'll import models later after setting up Flask app


def init_database() -> None:
    """Initialize the database with all tables.

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
