"""
Database configuration for the Side Quest Py application.

This module initializes the SQLAlchemy engine, session, and base model.
It also provides the dependency to get a database session.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.side_quest_py.api.config import settings

# Database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency to get a database session.

    Yields:
        Session: SQLAlchemy session that will be automatically closed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
