from dataclasses import dataclass, field
from typing import Set, Tuple


class AdventurerValidationError(Exception):
    """Raised when an adventurer fails validation."""

    pass


class AdventurerExperienceError(Exception):
    """Raised when there's an error related to experience gain or calculation."""

    pass


class AdventurerLevelError(Exception):
    """Raised when there's an error related to level calculations or leveling up."""

    pass


class AdventurerQuestError(Exception):
    """Raised when there's an error related to quest completion."""

    pass


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
            raise AdventurerLevelError(f"Invalid level type: {str(e)}")

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
            raise AdventurerLevelError(f"Invalid input type: {str(e)}")


@dataclass
class Adventurer:
    """
    An adventurer who goes on quests and gains experience!
    """

    name: str
    _level: int = field(default=1)
    experience: int = 0
    completed_quests: Set[str] = field(default_factory=set)
    level_calculator: LevelCalculator = field(default_factory=LevelCalculator)
    _has_leveled_up: bool = field(default=False)

    def __post_init__(self) -> None:
        """Validate the initial values when an adventurer is created."""
        try:
            if not self.name:
                raise AdventurerValidationError("Adventurer must have a name")
            if self.level < 1:
                raise AdventurerValidationError(
                    "Adventurer level cannot be a negative number or 0"
                )
            if self.experience < 0:
                raise AdventurerValidationError(
                    "Adventurer cannot have negative experience"
                )
        except TypeError as e:
            raise AdventurerValidationError(
                f"Invalid input type during initialization: {str(e)}"
            )

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the adventurer.

        Returns:
            str: A formatted string containing the adventurer's details.
        """
        try:
            quest_count = len(self.completed_quests)
            return f"{self.name} (Level {self.level}) - {self.experience} XP, {quest_count} quests completed"
        except Exception as e:
            return f"Error creating string representation: {str(e)}"

    @property
    def level(self) -> int:
        """
        Get the current level of the adventurer.

        Returns:
            int: Adventurer's current level.
        """
        return self._level

    @property
    def exp_for_next_level(self) -> int:
        """
        Get the experience required for the next level.

        Returns:
            int: Experience required for next level.
        """
        try:
            return self.level_calculator.calculate_req_exp(self.level)
        except AdventurerLevelError as e:
            raise AdventurerLevelError(
                f"Error calculating exp for next level: {str(e)}"
            )

    @property
    def exp_progress_percentage(self) -> float:
        """
        Get the progress towards the next level.

        Returns:
            float: Percentage progress towards next level (0 - 100).
        """
        try:
            required_exp = self.exp_for_next_level
            return (self.experience / required_exp) * 100 if required_exp > 0 else 100
        except ZeroDivisionError:
            return 100
        except Exception as e:
            raise AdventurerExperienceError(
                f"Error calculating progress percentage: {str(e)}"
            )

    def complete_quest(self, quest_id: str, experience_gain: int) -> Tuple[bool, bool]:
        """
        Process quest completion and experience gain.

        Args:
            quest_id: Unique id for the quest that was completed.
            experience_gain: Amount of experience earned by completing this quest.

        Returns:
            Tuple[bool, bool]: (was_new_completion, leveled_up)
                - was_new_completion: Whether this was a newly completed quest
                - leveled_up: Whether a level up occurred

        Raises:
            AdventurerQuestError: When the quest_id is empty or the experience_gain is negative.
        """
        try:
            if not quest_id:
                raise AdventurerQuestError("Quest ID cannot be empty")
            if experience_gain < 0:
                raise AdventurerQuestError("Experience gain cannot be negative")

            was_new = quest_id not in self.completed_quests
            self.completed_quests.add(quest_id)

            if was_new:
                self._reset_level_up_status()
                self.gain_experience(experience_gain)
                leveled_up = self.has_leveled_up()
            else:
                leveled_up = False

            return (was_new, leveled_up)

        except (TypeError, ValueError) as e:
            raise AdventurerQuestError(f"Error completing quest '{quest_id}': {str(e)}")
        except Exception as e:
            raise type(e)(
                f"Unexpected error occurred when completing quest '{quest_id}': {str(e)}"
            )

    def gain_experience(self, experience_gain: int) -> None:
        """
        Add experience to the adventurer.

        Args:
            experience_gain: Amount of experience gained by adventurer.

        Raises:
            AdventurerExperienceError: If the experience gained is negative.
        """
        try:
            if experience_gain < 0:
                raise AdventurerExperienceError("Experience gain cannot be negative")

            self.experience += experience_gain
            self._handle_level_up()

        except (TypeError, ValueError) as e:
            raise AdventurerExperienceError(f"Failed to gain experience: {str(e)}")
        except Exception as e:
            raise type(e)(
                f"Unexpected error occurred when gaining experience: {str(e)}"
            )

    def _handle_level_up(self) -> None:
        """
        Check for level up and handle the consequences if it occurs.
        """
        try:
            if self._check_level_up():
                self._reset_experience()
                self._has_leveled_up = True
        except AdventurerLevelError as e:
            raise AdventurerLevelError(f"Error handling level up: {str(e)}")

    def _reset_experience(self) -> None:
        """
        Reset the adventurer's experience to 0 after leveling up.
        """
        self.experience = 0

    def _reset_level_up_status(self) -> None:
        """
        Reset the level up status to False.
        This should be called before any new experience gain to track new level ups.
        """
        self._has_leveled_up = False

    def has_leveled_up(self) -> bool:
        """
        Check if the adventurer has leveled up based on current experience.

        Returns:
            bool: True if the adventurer has leveled up, False otherwise.
        """
        return self._has_leveled_up

    def get_exp_for_next_level(self, level: int) -> int:
        """
        Calculate the total exp required to reach the next level.

        Args:
            level (int): The current level of the adventurer.

        Returns:
            int: The amount of experience required to reach the next level.
        """
        try:
            return self.level_calculator.calculate_req_exp(level)
        except AdventurerLevelError as e:
            raise AdventurerLevelError(
                f"Error calculating exp for next level: {str(e)}"
            )

    def get_exp_progress(self) -> Tuple[int, int, float]:
        """
        Get details of current exp progress.

        Returns:
            Tuple[int, int, float]:
                - current exp
                - exp required for next level
                - percentage to next level
        """
        try:
            required_exp = self.get_exp_for_next_level(self.level)
            progress = (
                (self.experience / required_exp) * 100 if required_exp > 0 else 100
            )
            return (self.experience, required_exp, progress)
        except Exception as e:
            raise AdventurerExperienceError(f"Error calculating exp progress: {str(e)}")

    def _check_level_up(self) -> bool:
        """
        Check if adventurer has enough experience to level up.

        Returns:
            bool: Whether the adventurer leveled up.
        """
        try:
            if self.level_calculator.has_leveled_up(self.level, self.experience):
                self._level += 1
                return True
            return False
        except AdventurerLevelError as e:
            raise AdventurerLevelError(f"Error checking level up: {str(e)}")
