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
