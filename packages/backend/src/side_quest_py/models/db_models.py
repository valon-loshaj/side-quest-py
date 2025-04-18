"""
This module contains the SQLAlchemy models for the Side Quest application.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.side_quest_py.database import Base


class User(Base):  # type: ignore
    """SQLAlchemy model for users"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    auth_token = Column(String(128), nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship with adventurers
    adventurers = relationship("Adventurer", back_populates="user")


class Adventurer(db.Model):  # type: ignore
    """SQLAlchemy model for adventurers"""

    __tablename__ = "adventurers"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    adventurer_type = Column(String(100), default="default")
    leveled_up = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Foreign key to User
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Relationship with completed quests
    completed_quests = relationship("QuestCompletion", back_populates="adventurer")

    # Relationship with user
    user = relationship("User", back_populates="adventurers")


class Quest(db.Model):  # type: ignore
    """SQLAlchemy model for quests"""

    __tablename__ = "quests"

    id = Column(String(36), primary_key=True)
    adventurer_id = Column(String(36), ForeignKey("adventurers.id"), nullable=False)
    title = Column(String(200), nullable=False)
    experience_reward = Column(Integer, default=50)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship with adventurers who completed this quest
    completions = relationship("QuestCompletion", back_populates="quest")


class QuestCompletion(db.Model):  # type: ignore
    """SQLAlchemy model for tracking quest completions by adventurers"""

    __tablename__ = "quest_completions"

    id = Column(String(36), primary_key=True)
    adventurer_id = Column(String(36), ForeignKey("adventurers.id"), nullable=False)
    quest_id = Column(String(36), ForeignKey("quests.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    adventurer = relationship("Adventurer", back_populates="completed_quests")
    quest = relationship("Quest", back_populates="completions")
