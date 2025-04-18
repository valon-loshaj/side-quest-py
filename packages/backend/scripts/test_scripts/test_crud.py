#!/usr/bin/env python
"""Test CRUD operations with MariaDB database.

This script tests basic Create, Read, Update, Delete operations
using the application's models.
"""

import os
import sys
import uuid
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

# Import application database and models
from src.side_quest_py import db
from src.side_quest_py.models.db_models import User, Adventurer


def setup_app():
    """Set up a Flask app instance for testing."""
    app = Flask(__name__)

    # Configure the app
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL environment variable not set!")
        sys.exit(1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with our app
    db.init_app(app)

    return app


def test_create_user(app):
    """Test creating a user."""
    user_id = str(uuid.uuid4())
    username = f"testuser_{user_id[:8]}"

    with app.app_context():
        # Create a new user
        user = User(
            id=user_id, username=username, email=f"{username}@example.com", password_hash="pbkdf2:sha256:test_hash"
        )

        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ CREATE: Successfully created user {username}")
            return user_id
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ CREATE: Failed to create user: {e}")
            return None


def test_read_user(app, user_id):
    """Test reading a user."""
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if user:
                print(f"✅ READ: Found user {user.username} with email {user.email}")
                return user_id  # Return just the ID
            else:
                print(f"❌ READ: User with ID {user_id} not found")
                return None
        except SQLAlchemyError as e:
            print(f"❌ READ: Error querying user: {e}")
            return None


def test_update_user(app, user_id):
    """Test updating a user."""
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"❌ UPDATE: User with ID {user_id} not found")
                return False

            # Update the user's email
            new_email = f"updated_{user.username}@example.com"
            user.email = new_email
            db.session.commit()

            # Verify the update
            updated_user = User.query.get(user_id)
            if updated_user.email == new_email:
                print(f"✅ UPDATE: Successfully updated user email to {new_email}")
                return True
            else:
                print("❌ UPDATE: Email update verification failed")
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ UPDATE: Error updating user: {e}")
            return False


def test_create_adventurer(app, user_id):
    """Test creating an adventurer linked to a user."""
    with app.app_context():
        try:
            adventurer_id = str(uuid.uuid4())
            adventurer = Adventurer(id=adventurer_id, name="Test Adventurer", level=1, experience=0, user_id=user_id)
            db.session.add(adventurer)
            db.session.commit()
            print(f"✅ CREATE: Created adventurer {adventurer.name} (ID: {adventurer.id})")
            return adventurer_id
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ CREATE: Error creating adventurer: {e}")
            return None


def test_delete_user(app, user_id):
    """Test deleting a user."""
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"❌ DELETE: User with ID {user_id} not found")
                return False

            db.session.delete(user)
            db.session.commit()

            # Verify deletion
            deleted_user = User.query.get(user_id)
            if not deleted_user:
                print(f"✅ DELETE: Successfully deleted user {user_id}")
                return True
            else:
                print("❌ DELETE: User still exists after deletion")
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ DELETE: Error deleting user: {e}")
            return False


def run_tests():
    """Run all CRUD tests."""
    app = setup_app()

    print("\n===== Starting CRUD Tests =====\n")

    # Test CREATE
    user_id = test_create_user(app)
    if not user_id:
        print("❌ Cannot continue tests without a valid user")
        return

    # Test READ
    read_success = test_read_user(app, user_id)
    if not read_success:
        print("❌ Cannot continue tests without being able to read the user")
        return

    # Test UPDATE
    update_success = test_update_user(app, user_id)

    # Test creating related entity (Adventurer)
    adventurer_id = test_create_adventurer(app, user_id)

    # Test DELETE
    delete_success = test_delete_user(app, user_id)

    print("\n===== CRUD Test Summary =====")
    print(f"CREATE User: {'✅ Success' if user_id else '❌ Failed'}")
    print(f"READ User: {'✅ Success' if read_success else '❌ Failed'}")
    print(f"UPDATE User: {'✅ Success' if update_success else '❌ Failed'}")
    print(f"CREATE Adventurer: {'✅ Success' if adventurer_id else '❌ Failed'}")
    print(f"DELETE User: {'✅ Success' if delete_success else '❌ Failed'}")


if __name__ == "__main__":
    run_tests()
