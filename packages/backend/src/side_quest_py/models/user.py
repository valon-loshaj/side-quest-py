import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

from .adventurer import Adventurer


class UserValidationError(Exception):
    """Raised when a user fails validation."""


class UserNotFoundError(Exception):
    """Raised when a user is not found."""


class UserServiceError(Exception):
    """Raised when there's an error in the user service."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""


@dataclass
class User:
    """
    A user of the application.

    Attributes:
        username: The username of the user
        email: The email of the user
        id: The unique identifier for the user (set in service layer)
        created_at: The date and time the user was created
        updated_at: The date and time the user was last updated
        adventurers: Dictionary of adventurers associated with the user, keyed by adventurer ID
    """

    username: str
    email: str
    id: str
    password_hash: Optional[str] = None
    auth_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    adventurers: Dict[str, Adventurer] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate the initial values when a user is created.
        """
        self._validate_username()
        self._validate_email()

    def _validate_username(self) -> None:
        """Validate the username."""
        if not self.username or not self.username.strip():
            raise UserValidationError("Username cannot be empty")

    def _validate_email(self) -> None:
        """Validate the email."""
        if not self.email or not self.email.strip():
            raise UserValidationError("Email cannot be empty")

    def is_token_valid(self) -> bool:
        """Check if the user's authentication token is valid."""
        return self.auth_token is not None and self.token_expiry is not None and self.token_expiry > datetime.now()

    def generate_auth_token(self) -> str:
        """Generate a new authentication token with 24-hour expiry."""
        # Generate a secure random token
        alphabet = string.ascii_letters + string.digits
        self.auth_token = "".join(secrets.choice(alphabet) for _ in range(64))
        self.token_expiry = datetime.now() + timedelta(hours=24)
        return self.auth_token

    def invalidate_token(self) -> None:
        """Invalidate the current authentication token."""
        self.auth_token = None
        self.token_expiry = None

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the user.
        """
        return f"{self.username} (ID: {self.id})"

    def add_adventurer(self, adventurer: Adventurer) -> None:
        """Add an adventurer to the user."""
        self.adventurers[adventurer.id] = adventurer

    def remove_adventurer(self, adventurer_id: str) -> None:
        """Remove an adventurer from the user by ID."""
        if adventurer_id in self.adventurers:
            del self.adventurers[adventurer_id]

    def get_adventurer(self, adventurer_id: str) -> Optional[Adventurer]:
        """Get an adventurer by ID."""
        return self.adventurers.get(adventurer_id)

    def has_adventurer(self, adventurer_id: str) -> bool:
        """Check if the user has an adventurer with the given ID."""
        return adventurer_id in self.adventurers
