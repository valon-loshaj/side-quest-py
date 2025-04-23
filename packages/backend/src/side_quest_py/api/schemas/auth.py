"""
This module contains the schemas for the authentication endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema for the token response."""

    access_token: str
    token_type: str
    auth_token: str


class TokenData(BaseModel):
    """Schema for the token data."""

    username: Optional[str] = None


class UserBase(BaseModel):
    """Schema for the user base."""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for logging in a user."""

    username: str
    password: str


class UserResponse(UserBase):
    """Schema for the user response."""

    id: str
    created_at: datetime

    class Config:
        """Config for the user response."""

        from_attributes = True
