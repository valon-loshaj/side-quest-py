"""Database initialization script.

This script initializes the database and creates all tables.
"""

import os
import sys

import click
from flask import Flask
from flask.cli import with_appcontext
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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
            # Test database connection first
            connection = db.engine.connect()
            result = connection.execute(text("SELECT 1"))
            connection.close()
            print("✅ Database connection successful")

            # Now create all tables
            db.create_all()
            print("\n✅ Database initialized successfully")

            # List all tables created
            from sqlalchemy import inspect

            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables created: {tables}")

        except SQLAlchemyError as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
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
