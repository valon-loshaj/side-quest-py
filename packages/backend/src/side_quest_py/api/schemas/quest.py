"""
This module contains the schemas for the quest endpoints.
"""

from pydantic import BaseModel
from datetime import datetime


class QuestBase(BaseModel):
    """Schema for the quest."""

    title: str
    adventurer_id: str


class QuestCreate(QuestBase):
    """Schema for creating a quest."""

    title: str
    experience_reward: int | None = None
    adventurer_id: str


class QuestUpdate(BaseModel):
    """Schema for updating a quest."""

    title: str | None = None
    experience_reward: int | None = None
    completed: bool | None = None
    adventurer_id: str | None = None


class QuestResponse(QuestBase):
    """Schema for the quest response."""

    id: str
    adventurer_id: str
    title: str
    experience_reward: int
    completed: bool
    created_at: datetime
    updated_at: datetime
