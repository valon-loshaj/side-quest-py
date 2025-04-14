from datetime import datetime
from typing import Optional, Tuple
import os

import bcrypt
from flask import current_app

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
        try:
            # Check if token has valid JWT format
            parts = token.split(".")
            if len(parts) != 3:
                return None

            # Try direct JWT validation first - if it fails, we can skip the database lookup
            try:
                from .user_service import JWT_SECRET_KEY_FALLBACK
                import jwt

                # Get secret key
                secret_key = (
                    current_app.config.get("SECRET_KEY")
                    if current_app and current_app.config.get("SECRET_KEY")
                    else os.environ.get("SECRET_KEY", JWT_SECRET_KEY_FALLBACK)
                )

                # Now do actual validation
                jwt.decode(
                    token,
                    secret_key,
                    algorithms=["HS256"],
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": False,  # Disable iat verification to avoid clock skew issues
                        "leeway": 600,  # 10-minute leeway for clock skew
                    },
                )
            except jwt.ExpiredSignatureError:
                return None
            except jwt.InvalidTokenError:
                return None
            except (TypeError, ValueError) as e:
                raise AuthenticationError(f"Invalid token: {str(e)}") from e

            # Find the user with this token
            user = self.user_service.get_user_by_token(token)

            # If no user found with this token
            if not user:
                return None

            # Check database expiry
            token_expiry = user.token_expiry
            if token_expiry is None or token_expiry < datetime.now():  # type: ignore
                return None

            return user
        except Exception as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e

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
        try:
            if user.auth_token is None:
                return False

            # Import jwt from user_service
            from .user_service import jwt, JWT_SECRET_KEY_FALLBACK

            # Cast the auth_token to string to ensure compatibility with jwt.decode
            token_str = str(user.auth_token)

            # Get the secret key from Flask config if available
            secret_key = (
                current_app.config.get("SECRET_KEY")
                if current_app and current_app.config.get("SECRET_KEY")
                else os.environ.get("SECRET_KEY", JWT_SECRET_KEY_FALLBACK)
            )

            # Log token parts
            parts = token_str.split(".")

            if len(parts) != 3:
                return False

            try:
                # Decode and verify the token with clock skew tolerance
                payload = jwt.decode(
                    token_str,
                    secret_key,
                    algorithms=["HS256"],
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": False,  # Disable iat verification
                        # Allow for some clock skew (10 minutes)
                        "leeway": 600,
                    },
                )

                # Check if token has expired according to JWT claims
                if "exp" not in payload:
                    return False

                jwt_expiry = datetime.fromtimestamp(payload["exp"])
                current_time = datetime.now()
                jwt_valid = jwt_expiry > current_time

                if not jwt_valid:
                    return False

                # If token is valid according to JWT, also check the database expiry
                token_expiry = user.token_expiry
                if token_expiry is None:
                    return False

                # Force evaluation of the SQLAlchemy expression by comparing dates directly
                # Convert SQLAlchemy datetime to Python datetime
                token_expiry_dt = token_expiry
                if hasattr(token_expiry, "replace"):  # It's a datetime object
                    # Handle timezone if needed
                    if token_expiry.tzinfo is not None:
                        token_expiry_dt = token_expiry.replace(tzinfo=None)

                # Compare as Python datetime objects
                db_valid = token_expiry_dt > current_time

                if not db_valid:  # type: ignore
                    return False

                # Both JWT and database validation passed
                return True

            except jwt.ExpiredSignatureError:
                return False
            except jwt.InvalidTokenError:
                return False

        except (TypeError, ValueError) as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e
