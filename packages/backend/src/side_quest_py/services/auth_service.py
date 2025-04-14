from datetime import datetime
from typing import Optional, Tuple

import bcrypt

from .. import db
from ..models.db_models import User
from ..models.user import AuthenticationError, UserNotFoundError
from ..services.user_service import UserService


class AuthService:
    """Service for handling authentication-related operations."""

    def __init__(self, user_service: Optional[UserService] = None) -> None:
        """Initialize the auth service with a user service."""
        self.user_service = user_service if user_service else UserService()

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plain text password to hash

        Returns:
            str: The hashed password
        """
        # Generate a salt and hash the password
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Check if a plain text password matches the hashed version.

        Args:
            plain_password: The plain text password to check
            hashed_password: The hashed password to compare against

        Returns:
            bool: True if the passwords match, False otherwise
        """
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user with a hashed password.

        Args:
            username: The username for the new user
            email: The email for the new user
            password: The plain text password for the new user

        Returns:
            User: The newly created user object
        """
        try:
            # Create the user with the password
            user = self.user_service.create_user(username, email, password)
            return user
        except Exception as e:
            db.session.rollback()
            raise AuthenticationError(f"Error registering user: {str(e)}") from e

    def authenticate(self, username: str, password: str) -> Tuple[User, str]:
        """
        Authenticate a user with their username and password.

        Args:
            username: The username of the user
            password: The plain text password of the user

        Returns:
            Tuple[User, str]: The authenticated user and their new auth token

        Raises:
            AuthenticationError: If the authentication fails
        """
        try:
            # Use the user_service to authenticate
            user = self.user_service.authenticate_user(username, password)

            # Return the user and their token
            if not user.auth_token:  # type: ignore
                raise AuthenticationError("Failed to generate auth token")

            return user, user.auth_token  # type: ignore
        except UserNotFoundError as user_not_found_error:
            raise AuthenticationError("Invalid username or password") from user_not_found_error
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}") from e

    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate an authentication token and return the associated user.

        Args:
            token: The authentication token to validate

        Returns:
            Optional[User]: The user associated with the token if valid, None otherwise
        """
        # Find the user with this token
        user = self.user_service.get_user_by_token(token)

        if not user or not self._is_token_valid(user):
            return None

        return user

    def logout(self, user_id: str) -> None:
        """
        Logout a user by invalidating their authentication token.

        Args:
            user_id: The ID of the user to logout
        """
        try:
            self.user_service.invalidate_token(user_id)
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            raise AuthenticationError(f"Logout failed: {str(e)}") from e

    def _is_token_valid(self, user: User) -> bool:
        """Check if the user's token is valid and not expired."""
        return bool(
            user.auth_token is not None and user.token_expiry is not None and user.token_expiry > datetime.now()  # type: ignore
        )
