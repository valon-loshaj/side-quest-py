from typing import Optional, Tuple
import bcrypt

from ..models.user import User, AuthenticationError, UserNotFoundError
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
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Check if a plain text password matches the hashed version.

        Args:
            plain_password: The plain text password to check
            hashed_password: The hashed password to compare against

        Returns:
            bool: True if the passwords match, False otherwise
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
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
        # Create the user
        user = self.user_service.create_user(username, email)

        # Hash the password and store it
        user.password_hash = self.hash_password(password)

        return user

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
        # Find the user by username
        user = self.user_service.get_user_by_username(username)
        if not user:
            raise AuthenticationError("Invalid username or password")

        # Check the password
        if not user.password_hash or not self.check_password(password, user.password_hash):
            raise AuthenticationError("Invalid username or password")

        # Generate a new authentication token
        token = user.generate_auth_token()

        return user, token

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

        if not user or not user.is_token_valid():
            return None

        return user

    def logout(self, user_id: str) -> None:
        """
        Logout a user by invalidating their authentication token.

        Args:
            user_id: The ID of the user to logout
        """
        user = self.user_service.get_user(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID: {user_id} not found")

        user.invalidate_token()
