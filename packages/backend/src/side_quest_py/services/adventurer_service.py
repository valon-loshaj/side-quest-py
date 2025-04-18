from typing import Any, Dict, List, Optional

from .. import db
from ..models.adventurer import AdventurerValidationError, LevelCalculator
from ..models.db_models import Adventurer, QuestCompletion
from ulid import ULID


class AdventurerService:
    """Service for handling adventurer-related operations."""

    def __init__(self) -> None:
        """Initialize the adventurer service with a level calculator."""
        self.level_calculator = LevelCalculator()

    def create_adventurer(
        self, name: str, user_id: str, level: int = 1, experience: int = 0, adventurer_type: str = "default"
    ) -> Adventurer:
        """
        Create a new adventurer.

        Args:
            name: The name of the adventurer
            user_id: The ID of the user associated with the adventurer
            level: The starting level of the adventurer (default: 1)
            experience: The starting experience of the adventurer (default: 0)
        Returns:
            Adventurer: The newly created adventurer

        Raises:
            AdventurerValidationError: If the adventurer data is invalid
        """
        try:
            # Validate input data
            if not name:
                raise AdventurerValidationError("Adventurer must have a name")
            if level < 1:
                raise AdventurerValidationError("Level cannot be less than 1")
            if experience < 0:
                raise AdventurerValidationError("Experience cannot be negative")
            if not user_id:
                raise AdventurerValidationError("User ID cannot be empty")
            if not adventurer_type:
                raise AdventurerValidationError("Adventurer type cannot be empty")

            # Check if adventurer with the same name already exists
            existing = self.get_adventurer(name)
            if existing:
                raise AdventurerValidationError(f"Adventurer with name '{name}' already exists")

            # Create new adventurer with a generated ID
            adventurer = Adventurer(
                id=str(ULID()),
                name=name,
                level=level,
                experience=experience,
                user_id=user_id,
                adventurer_type=adventurer_type,
            )

            # Add to database
            db.session.add(adventurer)
            db.session.commit()

            return adventurer
        except AdventurerValidationError as e:
            db.session.rollback()
            raise e
        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise AdventurerValidationError(f"Error creating adventurer: {str(e)}") from e

    def get_adventurer(self, name: str) -> Optional[Adventurer]:
        """
        Get an adventurer by name.

        Args:
            name: The name of the adventurer

        Returns:
            Optional[Adventurer]: The adventurer if found, None otherwise
        """
        adventurer: Optional[Adventurer] = Adventurer.query.filter_by(name=name).first()
        return adventurer

    def get_all_adventurers(self) -> List[Adventurer]:
        """
        Get all adventurers.

        Returns:
            List[Adventurer]: A list of all adventurers
        """
        adventurers: List[Adventurer] = Adventurer.query.all()
        return adventurers

    def delete_adventurer(self, name: str) -> bool:
        """
        Delete an adventurer by name.

        Args:
            name: The name of the adventurer

        Returns:
            bool: True if the adventurer was deleted, False otherwise
        """
        adventurer = self.get_adventurer(name)
        if adventurer:
            try:
                db.session.delete(adventurer)
                db.session.commit()
                return True
            except (TypeError, ValueError) as e:
                db.session.rollback()
                raise AdventurerValidationError(f"Error deleting adventurer: {str(e)}") from e
        return False

    def update_adventurer(self, name: str, **kwargs: Any) -> Optional[Adventurer]:
        """
        Update an adventurer's attributes.

        Args:
            name: The name of the adventurer
            **kwargs: Attributes to update

        Returns:
            Optional[Adventurer]: The updated adventurer if found, None otherwise
        """
        adventurer = self.get_adventurer(name)
        if not adventurer:
            return None

        try:
            for key, value in kwargs.items():
                if hasattr(adventurer, key):
                    setattr(adventurer, key, value)

            db.session.commit()
            return adventurer
        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise AdventurerValidationError(f"Error updating adventurer: {str(e)}") from e

    def gain_experience(self, adventurer_name: str, experience_gain: int) -> Optional[Adventurer]:
        """
        Add experience to the adventurer and handle level up if necessary.

        Args:
            adventurer_name: Name of the adventurer gaining experience
            experience_gain: Amount of experience gained

        Returns:
            Optional[Adventurer]: The updated adventurer or None if not found

        Raises:
            AdventurerValidationError: If the experience gained is negative or other validation errors occur
        """
        if experience_gain < 0:
            raise AdventurerValidationError("Experience gain cannot be negative")

        adventurer = self.get_adventurer(adventurer_name)
        if not adventurer:
            return None

        try:
            adventurer.experience += experience_gain  # type: ignore

            required_exp = self.level_calculator.calculate_req_exp(adventurer.level)  # type: ignore
            if adventurer.experience >= required_exp:  # type: ignore
                adventurer.level += 1  # type: ignore
                adventurer.experience = 0  # type: ignore

            db.session.commit()
            return adventurer
        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise AdventurerValidationError(f"Error gaining experience: {str(e)}") from e

    def complete_quest(self, adventurer_name: str, quest_id: str, experience_gain: int) -> Optional[Dict[str, Any]]:
        """
        Process quest completion for an adventurer.

        Args:
            adventurer_name: Name of the adventurer completing the quest
            quest_id: ID of the quest being completed
            experience_gain: Experience gained from completing the quest

        Returns:
            Optional[Dict[str, Any]]: Result containing was_new_completion and leveled_up flags, or None if adventurer not found

        Raises:
            AdventurerValidationError: If there are validation errors with the quest completion
        """
        if not quest_id:
            raise AdventurerValidationError("Quest ID cannot be empty")
        if experience_gain < 0:
            raise AdventurerValidationError("Experience gain cannot be negative")

        adventurer = self.get_adventurer(adventurer_name)
        if not adventurer:
            return None

        try:
            completion = QuestCompletion.query.filter_by(adventurer_id=adventurer.id, quest_id=quest_id).first()

            was_new = completion is None

            if was_new:
                new_completion = QuestCompletion(adventurer_id=adventurer.id, quest_id=quest_id)
                db.session.add(new_completion)

                old_level = adventurer.level

                adventurer.experience += experience_gain  # type: ignore

                required_exp = self.level_calculator.calculate_req_exp(old_level)  # type: ignore
                leveled_up = False

                if adventurer.experience >= required_exp:  # type: ignore
                    adventurer.level += 1  # type: ignore
                    adventurer.experience = 0  # type: ignore
                    leveled_up = True

                db.session.commit()

                return {"was_new_completion": True, "leveled_up": leveled_up}
            else:
                return {"was_new_completion": False, "leveled_up": False}

        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise AdventurerValidationError(f"Error completing quest: {str(e)}") from e

    def adventurer_to_dict(self, adventurer: Adventurer) -> Dict[str, Any]:
        """
        Convert an adventurer to a dictionary for JSON serialization.

        Args:
            adventurer: The adventurer to convert

        Returns:
            Dict[str, Any]: A dictionary representation of the adventurer
        """
        experience_for_next_level = self.level_calculator.calculate_req_exp(adventurer.level)  # type: ignore

        progress_percentage = (
            (adventurer.experience / experience_for_next_level * 100) if experience_for_next_level > 0 else 100
        )

        completed_quests = [
            completion.quest_id for completion in QuestCompletion.query.filter_by(adventurer_id=adventurer.id).all()
        ]

        return {
            "id": adventurer.id,
            "name": adventurer.name,
            "level": adventurer.level,
            "adventurer_type": adventurer.adventurer_type,
            "experience": adventurer.experience,
            "experience_for_next_level": experience_for_next_level,
            "progress_percentage": round(progress_percentage, 2),  # type: ignore
            "completed_quests_count": len(completed_quests),
            "completed_quests": completed_quests,
        }
