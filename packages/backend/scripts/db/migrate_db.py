#!/usr/bin/env python
"""Database migration script.

This script initializes and runs migrations for the database.
"""

import os
import sys
import click
from flask import Flask
from flask.cli import with_appcontext
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_app():
    """Set up a Flask app instance for migrations."""
    # Get the environment from environment variable, default to development
    env = os.environ.get("FLASK_ENV", "development")
    print(f"Environment: {env}")

    # Import application components
    from src.side_quest_py import db
    from src.side_quest_py.config import config

    # Create a Flask app
    app = Flask(__name__)

    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL environment variable not set!")
        sys.exit(1)

    print(f"Using DATABASE_URL: {database_url}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with our app
    db.init_app(app)

    # Import models to ensure they're registered with SQLAlchemy
    from src.side_quest_py.models import Adventurer, Quest, QuestCompletion, User

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    return app, migrate


def init_migrations():
    """Initialize database migrations."""
    app, migrate = setup_app()

    with app.app_context():
        try:
            # Check if migrations directory exists
            migrations_dir = os.path.join(os.getcwd(), "migrations")
            if not os.path.exists(migrations_dir):
                print("Initializing migrations directory...")
                os.system(f"flask db init")
                print("✅ Migrations directory initialized")
            else:
                print("Migrations directory already exists")

            # Create a migration
            print("Creating migration...")
            os.system(f"flask db migrate -m 'Initial migration'")
            print("✅ Migration created")

            # Apply the migration
            print("Applying migration...")
            os.system(f"flask db upgrade")
            print("✅ Migration applied")

        except SQLAlchemyError as e:
            print(f"❌ Database error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


@click.command("migrate-db")
@with_appcontext
def migrate_db_command():
    """Flask CLI command to migrate the database."""
    click.echo("Running database migrations...")
    init_migrations()
    click.echo("Database migrations complete!")


if __name__ == "__main__":
    print("Starting database migrations...")
    init_migrations()
