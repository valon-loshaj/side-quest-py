from typing import Any, Dict, List, Optional

from ..models.user import User, UserNotFoundError, UserServiceError, UserValidationError
from ..models.adventurer import AdventurerNotFoundError
from ..services.adventurer_service import AdventurerService

class UserService:
    """Service for handling user-related operations."""

    def __init__(self) -> None:
        """Initialize the user service with an in-memory store."""
        self.users: Dict[str, User] = {}

    def create_user(self, username: str, email: str) -> User:
        """
        Create a new user.

        Args:
            username: The username of the user
            email: The email of the user
        """
        try:
            user = User(username=username, email=email)
            self.users[user.id] = user
            return user
        except UserValidationError as e:
            raise e
        except Exception as e:
            raise UserServiceError(f"Error creating user: {str(e)}") from e

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            user_id: The ULID string ID of the user
        """
        try:
            return self.users.get(user_id)
        except Exception as e:
            raise UserNotFoundError(f"User with ID: {user_id} not found") from e

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by their username.

        Args:
            username: The username of the user
        """
        try:
            for user in self.users.values():
                if user.username == username:
                    return user
            return None
        except Exception as e:
            raise UserNotFoundError(f"User with username: {username} not found") from e

    def get_user_by_token(self, token: str) -> Optional[User]:
        """
        Get a user by their authentication token.

        Args:
            token: The authentication token of the user
        """
        try:
            for user in self.users.values():
                if user.auth_token == token:
                    return user
            return None
        except Exception as e:
            raise UserNotFoundError(f"Error: User with token: {token} not found. {e}") from e

    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self.users.values())

    def update_user(self, user_id: str, username: Optional[str] = None, email: Optional[str] = None) -> User:
        """
        Update a user's information.

        Args:
            user_id: The ULID string ID of the user
            username: The new username for the user
            email: The new email for the user
        """
        try:
            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")
            if username:
                user.username = username
            if email:
                user.email = email
            return user
        except UserNotFoundError as e:
            raise e
        except Exception as e:
            raise UserServiceError(f"Error updating user: {str(e)}") from e

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user by their ID.

        Args:
            user_id: The ULID string ID of the user
        """
        try:
            del self.users[user_id]
        except Exception as e:
            raise UserServiceError(f"Error deleting user: {str(e)}") from e

    def add_adventurer(self, user_id: str, adventurer_id: str) -> User:
        """
        Add an adventurer to a user.

        Args:
            user_id: The ULID string ID of the user 
            adventurer_id: The ULID string ID of the adventurer
        """
        try:
            adventurer_service = AdventurerService()
            user = self.get_user(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID: {user_id} not found")
            adventurer = adventurer_service.get_adventurer(adventurer_id)
            if adventurer is None:
                raise AdventurerNotFoundError(f"Adventurer with ID: {adventurer_id} not found")
            user.adventurers.append(adventurer)
            return user
        except (TypeError, ValueError) as e:
            raise UserServiceError(f"Error adding adventurer to user: {str(e)}") from e

    def user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert a User object to a dictionary.

        Args:
            user: The User object to convert
        """
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "adventurers": [adventurer.name for adventurer in user.adventurers],
        }

        # Include auth token and expiry if they exist
        if user.auth_token:
            user_dict["auth_token"] = user.auth_token
            if user.token_expiry:
                user_dict["token_expiry"] = user.token_expiry.isoformat()

        return user_dict
