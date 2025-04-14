import secrets
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import bcrypt
import jwt
from ulid import ULID
from flask import current_app

from .. import db
from ..models.adventurer import AdventurerNotFoundError
from ..models.db_models import Adventurer, User
from ..models.user import UserNotFoundError, UserServiceError, UserValidationError
from ..services.adventurer_service import AdventurerService

# Actual secret key retrieved from Flask config at runtime
# This is just a fallback
JWT_SECRET_KEY_FALLBACK = "development_fallback_key"


class UserService:
    """Service for handling user-related operations."""

    def create_user(self, username: str, email: str, password: str) -> User:
        """
        Create a new user.

        Args:
            username: The username of the user
            email: The email of the user
            password: The password of the user
        """
        try:
            # Check if user with the same username already exists
            existing_user = self.get_user_by_username(username)
            if existing_user:
                raise UserValidationError(f"User with username '{username}' already exists")

            # Check if user with the same email already exists
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                raise UserValidationError(f"User with email '{email}' already exists")

            # Generate a ULID for the user ID
            user_id = str(ULID())

            # Create new user
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=self._hash_password(password),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Add to database
            db.session.add(user)
            db.session.commit()

            return user
        except UserValidationError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error creating user: {str(e)}") from e

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            user_id: The string ID of the user
        """
        try:
            user: Optional[User] = User.query.get(user_id)
            return user
        except Exception as e:
            raise UserNotFoundError(f"User with ID: {user_id} not found") from e

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by their username.

        Args:
            username: The username of the user
        """
        try:
            user: Optional[User] = User.query.filter_by(username=username).first()
            return user
        except Exception as e:
            raise UserNotFoundError(f"User with username: {username} not found") from e

    def get_user_by_token(self, token: str) -> Optional[User]:
        """
        Get a user by their authentication token.

        Args:
            token: The authentication token of the user

        Returns:
            Optional[User]: The user with the token or None if not found
        """
        try:
            # Find user with this token
            user: Optional[User] = User.query.filter_by(auth_token=token).first()
            return user
        except Exception as e:
            raise UserNotFoundError(f"Error: User with token not found. {e}") from e

    def get_all_users(self) -> List[User]:
        """Get all users."""
        users: List[User] = User.query.all()
        return users

    def update_user(
        self, user_id: str, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None
    ) -> User:
        """
        Update a user's information.

        Args:
            user_id: The string ID of the user
            username: The new username for the user
            email: The new email for the user
            password: The new password for the user
        """
        try:
            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")

            # Check username uniqueness if changing
            if username and username != user.username:
                existing = User.query.filter_by(username=username).first()
                if existing and existing.id != user_id:
                    raise UserValidationError(f"Username '{username}' is already taken")
                user.username = username  # type: ignore

            # Check email uniqueness if changing
            if email and email != user.email:
                existing = User.query.filter_by(email=email).first()
                if existing and existing.id != user_id:
                    raise UserValidationError(f"Email '{email}' is already in use")
                user.email = email  # type: ignore

            # Update password if provided
            if password:
                user.password_hash = self._hash_password(password)  # type: ignore

            # Update timestamp
            user.updated_at = datetime.now()  # type: ignore

            db.session.commit()
            return user
        except (UserNotFoundError, UserValidationError) as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error updating user: {str(e)}") from e

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user by their ID.

        Args:
            user_id: The string ID of the user

        Returns:
            bool: True if the user was deleted
        """
        try:
            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")

            db.session.delete(user)
            db.session.commit()
            return True
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error deleting user: {str(e)}") from e

    def add_adventurer(self, user_id: str, adventurer_name: str) -> User:
        """
        Associate an existing adventurer with a user.

        Args:
            user_id: The string ID of the user
            adventurer_name: The name of the adventurer

        Returns:
            User: The updated user
        """
        try:
            adventurer_service = AdventurerService()

            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")

            adventurer = adventurer_service.get_adventurer(adventurer_name)
            if adventurer is None:
                raise AdventurerNotFoundError(f"Adventurer with name: {adventurer_name} not found")

            # Update the adventurer's user_id
            adventurer.user_id = user_id  # type: ignore

            # Update timestamp
            user.updated_at = datetime.now()  # type: ignore

            db.session.commit()
            return user
        except (UserNotFoundError, AdventurerNotFoundError) as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error adding adventurer to user: {str(e)}") from e

    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user with username and password.

        Args:
            username: The username of the user
            password: The password of the user

        Returns:
            User: The authenticated user

        Raises:
            UserNotFoundError: If user not found
            UserValidationError: If authentication fails
        """
        try:
            user = self.get_user_by_username(username)
            if user is None:
                raise UserNotFoundError(f"User with username: {username} not found")

            # Verify the password using bcrypt
            if not user.password_hash or not self._check_password(password, user.password_hash):  # type: ignore
                raise UserValidationError("Invalid username or password")

            # Generate new auth token with JWT
            token = self._generate_auth_token()

            # Calculate token expiry time - same as in the JWT payload (24 hours)
            expiry = datetime.now() + timedelta(hours=24)

            # Save token and expiry to user
            user.auth_token = token  # type: ignore
            user.token_expiry = expiry  # type: ignore

            db.session.commit()
            return user
        except (UserNotFoundError, UserValidationError) as e:
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error authenticating user: {str(e)}") from e

    def set_password(self, user_id: str, password: str) -> User:
        """
        Set or update a user's password.

        Args:
            user_id: The ID of the user
            password: The new password (will be hashed)

        Returns:
            User: The updated user
        """
        try:
            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")

            # Hash the password
            user.password_hash = self._hash_password(password)  # type: ignore
            user.updated_at = datetime.now()  # type: ignore

            db.session.commit()
            return user
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error setting password: {str(e)}") from e

    def invalidate_token(self, user_id: str) -> bool:
        """
        Invalidate a user's authentication token (logout).

        Args:
            user_id: The ID of the user

        Returns:
            bool: True if successful
        """
        try:
            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")

            user.auth_token = None  # type: ignore
            user.token_expiry = None  # type: ignore

            db.session.commit()
            return True
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Error invalidating token: {str(e)}") from e

    def user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert a User object to a dictionary.

        Args:
            user: The User object to convert
        """
        # Get the user's adventurers
        adventurers = Adventurer.query.filter_by(user_id=user.id).all()

        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "adventurers": [adventurer.name for adventurer in adventurers],
            "created_at": user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else None,
            "updated_at": user.updated_at.isoformat() if hasattr(user.updated_at, "isoformat") else None,
        }

        # Include auth token and expiry if they exist
        if user.auth_token is not None:
            user_dict["auth_token"] = user.auth_token
            if user.token_expiry is not None:
                user_dict["token_expiry"] = (
                    user.token_expiry.isoformat() if hasattr(user.token_expiry, "isoformat") else None
                )

        return user_dict

    def _generate_auth_token(self) -> str:
        """Generate a JWT token with expiration time."""
        # Set expiration time to 24 hours from now
        now = datetime.utcnow()
        expiry = now + timedelta(hours=24)

        # Create the payload with subject, issued at, and expiration time
        payload = {
            "sub": str(secrets.token_hex(8)),  # Unique identifier
            # Remove iat claim to avoid issues with clock skew
            "exp": int(expiry.timestamp()),  # Using integer timestamp to avoid precision issues
            "type": "auth",
        }

        # Get the secret key from Flask app config if available
        secret_key = (
            current_app.config["SECRET_KEY"] if current_app else os.environ.get("SECRET_KEY", JWT_SECRET_KEY_FALLBACK)
        )

        # Generate the JWT token
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        # Handle bytes vs string conversion based on jwt version
        if isinstance(token, bytes):
            token_str = token.decode("utf-8")
            return token_str
        else:
            return token

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def _check_password(self, plain_password: str, hashed_password: str) -> bool:
        """Check if a plain text password matches the hashed version."""
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
