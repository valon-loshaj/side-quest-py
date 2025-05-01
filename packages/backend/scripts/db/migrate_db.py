#!/usr/bin/env python
"""Database migration script.

This script initializes and runs migrations for the database.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path to make imports work
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent.parent
sys.path.insert(0, str(root_dir))

import click
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import settings
from src.side_quest_py.api.config import settings


def run_alembic_command(command):
    """Run an alembic command through subprocess.

    Args:
        command: The alembic command to run
    """
    try:
        subprocess.run(["alembic"] + command.split(), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running alembic command: {e}")
        return False


def init_migrations():
    """Initialize database migrations using Alembic."""
    # Get the environment from environment variable
    env = os.environ.get("FASTAPI_ENV", "development")
    print(f"Environment: {env}")

    # Get database URL from environment
    database_url = settings.DATABASE_URL
    print(f"Using DATABASE_URL: {database_url}")

    # Import models to ensure they're registered with SQLAlchemy
    from src.side_quest_py.models.db_models import Adventurer, Quest, QuestCompletion, User

    try:
        # Check if alembic.ini exists
        if not os.path.exists("alembic.ini"):
            print("Initializing alembic...")
            if not run_alembic_command("init migrations"):
                print("❌ Failed to initialize alembic")
                sys.exit(1)
            print("✅ Alembic initialized")
        else:
            print("Alembic already initialized")

        # Create a migration
        print("Creating migration...")
        if not run_alembic_command("revision --autogenerate -m 'Migration'"):
            print("❌ Failed to create migration")
            sys.exit(1)
        print("✅ Migration created")

        # Apply the migration
        print("Applying migration...")
        if not run_alembic_command("upgrade head"):
            print("❌ Failed to apply migration")
            sys.exit(1)
        print("✅ Migration applied")

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Starting database migrations...")
    init_migrations()
