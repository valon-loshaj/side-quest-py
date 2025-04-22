"""
This module contains the schemas for the adventurer endpoints.
"""

from pydantic import BaseModel
from datetime import datetime


class AdventurerBase(BaseModel):
    """Schema for the adventurer."""

    name: str
    adventurer_type: str


class AdventurerCreate(AdventurerBase):
    """Schema for creating an adventurer."""

    name: str
    adventurer_type: str


class AdventurerUpdate(BaseModel):
    """Schema for updating an adventurer."""

    name: str | None = None
    level: int | None = None
    experience: int | None = None
    adventurer_type: str | None = None


class AdventurerResponse(AdventurerBase):
    """Schema for the adventurer response."""

    id: str
    name: str
    level: int
    experience: int
    adventurer_type: str
    created_at: datetime
    updated_at: datetime
