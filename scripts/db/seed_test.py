"""Test script for database seeding functionality."""
import os
import sys

# Add the root directory to the path to import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.side_quest_py import create_app
from src.side_quest_py.db_utils import reset_db, seed_db

def main():
    """Create the app, reset the database, and seed it."""
    app = create_app()
    with app.app_context():
        # Reset the database
        print("Resetting database...")
        reset_db()
        
        # Seed the database
        print("Seeding database...")
        seed_db()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    main()
