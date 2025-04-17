from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from ulid import ULID

from .quest_completion import QuestCompletion


class AdventurerValidationError(Exception):
    """Raised when an adventurer fails validation."""


class AdventurerExperienceError(Exception):
    """Raised when there's an error related to experience gain or calculation."""


class AdventurerLevelError(Exception):
    """Raised when there's an error related to level calculations or leveling up."""


class AdventurerQuestError(Exception):
    """Raised when there's an error related to quest completion."""


class AdventurerNotFoundError(Exception):
    """Raised when an adventurer is not found."""


class LevelCalculator:
    """Handles the logic necessary when an adventurer levels up"""

    def calculate_req_exp(self, level: int) -> int:
        """
        Calculate the experience needed to reach the next level.

        Args:
            level (int): The next level we are trying to calculate the req experience to reach.

        Raises:
            AdventurerLevelError: If the level is less than 1 or invalid type.

        Returns:
            int: The amount of experience required to reach that level.
        """
        try:
            if level < 1:
                raise AdventurerLevelError("Level must be greater than 0")
            return level * 100
        except TypeError as e:
            raise AdventurerLevelError(f"Invalid level type: {str(e)}") from e

    def has_leveled_up(self, level: int, experience_gain: int) -> bool:
        """
        Check if an adventurer has leveled up.

        Args:
            level (int): The current level of the adventurer.
            experience_gain (int): The experience gained by the adventurer.

        Raises:
            AdventurerLevelError: If the current level is less than 1.
            AdventurerExperienceError: If the experience gained is negative.

        Returns:
            bool: Whether the adventurer has leveled up.
        """
        try:
            if level < 1:
                raise AdventurerLevelError("Level must be greater than 0")
            if experience_gain < 0:
                raise AdventurerExperienceError("Experience cannot be negative")

            required_exp = self.calculate_req_exp(level)
            return experience_gain >= required_exp
        except TypeError as e:
            raise AdventurerLevelError(f"Invalid input type: {str(e)}") from e


@dataclass
class Adventurer:
    """
    An adventurer is a character that can complete quests.
    """

    name: str
    user_id: str
    id: str = field(default_factory=lambda: str(ULID()))
    level: int = field(default=1)
    experience: int = field(default=0)
    adventurer_type: str = field(default="default")
    completed_quests: List[QuestCompletion] = field(default_factory=list)
    leveled_up: bool = field(default=False)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """
        Validate the initial values when an adventurer is created.
        """
        try:
            self._validate_name()
            self._validate_level()
            self._validate_experience()
            self._validate_user_id()
            self._validate_adventurer_type()

        except ValueError as e:
            raise AdventurerValidationError(f"Error validating adventurer: {str(e)}") from e
        except Exception as e:
            raise AdventurerValidationError(f"Unexpected error occurred when validating adventurer: {str(e)}") from e

    def _validate_name(self) -> None:
        """Validate the adventurer's name."""
        if not self.name or not self.name.strip():
            raise AdventurerValidationError("Adventurer name cannot be empty")

    def _validate_level(self) -> None:
        """Validate the adventurer's level."""
        if not isinstance(self.level, int) or self.level < 1:
            raise AdventurerLevelError("Level must be a positive integer")

    def _validate_experience(self) -> None:
        """Validate the adventurer's experience."""
        if not isinstance(self.experience, int) or self.experience < 0:
            raise AdventurerExperienceError("Experience must be a non-negative integer")

    def _validate_completed_quests(self) -> None:
        """Validate the adventurer's completed quests."""
        if not isinstance(self.completed_quests, list):
            raise AdventurerQuestError("Completed quests must be a list")

    def _validate_user_id(self) -> None:
        """Validate the adventurer's user ID."""
        if not isinstance(self.user_id, str) or not self.user_id.strip():
            raise AdventurerValidationError("User ID cannot be empty")

    def _validate_adventurer_type(self) -> None:
        """Validate the adventurer's type."""
        if not isinstance(self.adventurer_type, str) or not self.adventurer_type.strip():
            raise AdventurerValidationError("Adventurer type cannot be empty")
