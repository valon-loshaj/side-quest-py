"""Database utility functions for the application."""
from typing import Optional
import logging

from flask import Flask, current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Import the SQLAlchemy instance directly
from . import db

def init_db(app: Optional[Flask] = None) -> None:
    """Initialize the database by creating all tables.
    
    Args:
        app: Flask application instance (optional)
    """
    # Get the app if not provided
    if app is None:
        app = current_app
    
    db.create_all()
    logging.info(f"Database initialized: {app.config['SQLALCHEMY_DATABASE_URI']}")


def reset_db(app: Optional[Flask] = None) -> None:
    """Reset the database by dropping and recreating all tables.
    
    Args:
        app: Flask application instance (optional)
    """
    # Get the app if not provided
    if app is None:
        app = current_app
    
    db.drop_all()
    db.create_all()
    logging.info(f"Database reset: {app.config['SQLALCHEMY_DATABASE_URI']}")


def seed_db(app: Optional[Flask] = None) -> None:
    """Seed the database with initial data.
    
    Args:
        app: Flask application instance (optional)
    """
    # Get the app if not provided
    if app is None:
        app = current_app
    
    try:
        from .models.db_models import User, Adventurer, Quest
        
        # Add seed data logic here
        # Example:
        # if User.query.count() == 0:
        #     admin = User(username="admin", email="admin@example.com")
        #     admin.set_password("password")
        #     db.session.add(admin)
        #     db.session.commit()
        
        logging.info("Database seeded successfully")
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error seeding database: {e}")
        raise


def get_db_status(app: Optional[Flask] = None) -> dict:
    """Get the status of the database.
    
    Args:
        app: Flask application instance (optional)
        
    Returns:
        dict: Database status information
    """
    # Get the app if not provided
    if app is None:
        app = current_app
    
    # Get database URI and environment info first in case db connection fails
    env = app.config.get("ENV") or app.config.get("FLASK_ENV", "development")
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "not_configured")
    track_modifications = app.config.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    
    try:
        db.session.execute(text("SELECT 1"))
        status = "connected"
    except Exception as e:
        status = f"error: {str(e)}"

    return {
        "status": status,
        "uri": uri,
        "track_modifications": track_modifications,
        "env": env
    } 