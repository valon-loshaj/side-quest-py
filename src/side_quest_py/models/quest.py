from dataclasses import dataclass, field
from datetime import datetime

from ulid import ULID


class QuestValidationError(Exception):
    """Raised when a quest fails validation."""


class QuestCompletionError(Exception):
    """Raised when there's an error completing a quest."""


class QuestNotFoundError(Exception):
    """Raised when a quest is not found."""


class QuestServiceError(Exception):
    """Raised when there's an error in the quest service."""


@dataclass
class Quest:
    """
    A quest that an adventurer can complete.

    Attributes:
        title: The title of the quest
        experience_reward: The experience points awarded for completing the quest
        id: Unique identifier for the quest (auto-generated)
        completed: Whether the quest has been completed
    """

    title: str
    adventurer_id: str
    experience_reward: int = field(default=50)
    id: str = field(default_factory=lambda: str(ULID()))
    completed: bool = field(default=False)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """
        Validate the initial values when a quest is created.
        Raises:
            QuestValidationError: If the quest data is invalid
        """
        try:
            self._validate_title()
            self._validate_experience_reward()
            self._validate_adventurer_id()
        except ValueError as e:
            raise QuestValidationError(f"Error validating quest: {str(e)}") from e
        except Exception as e:
            raise QuestValidationError(f"Unexpected error occurred when validating quest: {str(e)}") from e

    def _validate_title(self) -> None:
        """Validate the quest title."""
        if not self.title or not self.title.strip():
            raise QuestValidationError("Quest title cannot be empty")

    def _validate_experience_reward(self) -> None:
        """Validate the experience reward."""
        if self.experience_reward < 0:
            raise QuestValidationError("Experience reward cannot be negative")

    def _validate_adventurer_id(self) -> None:
        """Validate the adventurer ID."""
        if not self.adventurer_id or not self.adventurer_id.strip():
            raise QuestValidationError("Adventurer ID cannot be empty")

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the quest.

        Returns:
            str: A formatted string containing the quest title and ID
        """
        return f"{self.title} (ID: {self.id})"

    def complete(self) -> None:
        """
        Mark the quest as completed.

        Raises:
            QuestCompletionError: If the quest is already completed
        """
        try:
            if self.completed:
                raise QuestCompletionError("Quest is already completed")
            self.completed = True
        except ValueError as e:
            raise QuestCompletionError(f"Error completing quest: {str(e)}") from e
        except Exception as e:
            raise QuestCompletionError(f"Unexpected error occurred when completing quest: {str(e)}") from e

    @property
    def is_completed(self) -> bool:
        """
        Check if the quest has been completed.

        Returns:
            bool: True if the quest is completed, False otherwise
        """
        try:
            return self.completed
        except Exception as e:
            raise ValueError(f"Error checking if quest is completed: {str(e)}") from e
