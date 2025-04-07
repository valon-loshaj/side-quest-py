from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# Import db from the Flask application
from .. import db


class Adventurer(db.Model):  # type: ignore
    """SQLAlchemy model for adventurers"""
    __tablename__ = 'adventurers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # Relationship with completed quests
    completed_quests = relationship("QuestCompletion", back_populates="adventurer")


class Quest(db.Model):  # type: ignore
    """SQLAlchemy model for quests"""
    __tablename__ = 'quests'
    
    id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    experience_reward = Column(Integer, default=50)
    completed = Column(Boolean, default=False)
    
    # Relationship with adventurers who completed this quest
    completions = relationship("QuestCompletion", back_populates="quest")


class QuestCompletion(db.Model):  # type: ignore
    """SQLAlchemy model for tracking quest completions by adventurers"""
    __tablename__ = 'quest_completions'
    
    id = Column(Integer, primary_key=True)
    adventurer_id = Column(Integer, ForeignKey('adventurers.id'), nullable=False)
    quest_id = Column(String(36), ForeignKey('quests.id'), nullable=False)
    
    # Relationships
    adventurer = relationship("Adventurer", back_populates="completed_quests")
    quest = relationship("Quest", back_populates="completions") 