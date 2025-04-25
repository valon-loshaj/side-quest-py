from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from ulid import ULID

from src.side_quest_py.database import get_db
from src.side_quest_py.models.adventurer import (
    AdventurerValidationError,
    LevelCalculator,
    AdventurerNotFoundError,
    AdventurerDeletionError,
)
from src.side_quest_py.models.db_models import Adventurer
from src.side_quest_py.tasks.email_tasks import send_level_up_email


class AdventurerService:
    """Service for handling adventurer-related operations."""

    def __init__(self, db: Session = Depends(get_db)) -> None:
        """Initialize the adventurer service with a level calculator."""
        self.level_calculator = LevelCalculator()
        self.db = db

    async def create_adventurer(
        self, name: str, user_id: str, level: int = 1, experience: int = 0, adventurer_type: str = "Amazon"
    ) -> Adventurer:
        """
        Create a new adventurer.

        Args:
            name: The name of the adventurer
            user_id: The ID of the user associated with the adventurer
            level: The starting level of the adventurer (default: 1)
            experience: The starting experience of the adventurer (default: 0)
            adventurer_type: The type of adventurer to create (default: "default") Returns:
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

            adventurer = Adventurer(
                id=str(ULID()),
                name=name,
                level=level,
                experience=experience,
                user_id=user_id,
                adventurer_type=adventurer_type,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Add to database
            self.db.add(adventurer)
            self.db.commit()

            return adventurer
        except AdventurerValidationError as e:
            self.db.rollback()
            raise e
        except (TypeError, ValueError) as e:
            self.db.rollback()
            raise AdventurerValidationError(f"Error creating adventurer: {str(e)}") from e

    async def get_adventurer_by_id(self, adventurer_id: str) -> Optional[Adventurer]:
        """
        Get an adventurer by ID.

        Args:
            adventurer_id: The ID of the adventurer

        Returns:
            Optional[Adventurer]: The adventurer if found, None otherwise
        """
        adventurer: Optional[Adventurer] = self.db.query(Adventurer).filter_by(id=adventurer_id).first()
        return adventurer

    async def get_all_adventurers(self, user_id: str) -> List[Adventurer]:
        """
        Get all adventurers for a user.

        Returns:
            List[Adventurer]: A list of all adventurers
        """
        adventurers: List[Adventurer] = self.db.query(Adventurer).filter_by(user_id=user_id).all()
        return adventurers

    async def delete_adventurer(self, adventurer_id: str) -> bool:
        """
        Delete an adventurer by ID.

        Args:
            adventurer_id: The ID of the adventurer to delete

        Returns:
            bool: True if the adventurer was deleted, False otherwise
        """
        adventurer = await self.get_adventurer_by_id(adventurer_id)
        if adventurer:
            try:
                self.db.delete(adventurer)
                self.db.commit()
                return True
            except (TypeError, ValueError) as e:
                self.db.rollback()
                raise AdventurerValidationError(f"Error deleting adventurer: {str(e)}") from e
            except Exception as e:
                self.db.rollback()
                raise AdventurerDeletionError(f"Unexpected error deleting adventurer: {str(e)}") from e
        return False

    async def update_adventurer(self, adventurer_id: str, **kwargs: Any) -> Optional[Adventurer]:
        """
        Update an adventurer's attributes by ID.

        Args:
            adventurer_id: The ID of the adventurer to update
            **kwargs: Attributes to update

        Returns:
            Optional[Adventurer]: The updated adventurer if found, None otherwise
        """
        adventurer = self.db.query(Adventurer).filter_by(id=adventurer_id).first()
        if not adventurer:
            return None

        try:
            for key, value in kwargs.items():
                if hasattr(adventurer, key):
                    setattr(adventurer, key, value)

            self.db.commit()
            return adventurer
        except (TypeError, ValueError) as e:
            self.db.rollback()
            raise AdventurerValidationError(f"Error updating adventurer: {str(e)}") from e

    async def gain_experience(self, adventurer_id: str, experience_gain: int) -> Optional[Adventurer]:
        """
        Add experience to the adventurer and handle level up if necessary.

        Args:
            adventurer_id: ID of the adventurer gaining experience
            experience_gain: Amount of experience gained

        Returns:
            Optional[Adventurer]: The updated adventurer or None if not found

        Raises:
            AdventurerValidationError: If the experience gained is negative or other validation errors occur
        """

        if experience_gain < 0:
            raise AdventurerValidationError("Experience gain cannot be negative")

        adventurer = await self.get_adventurer_by_id(adventurer_id)
        if not adventurer:
            raise AdventurerNotFoundError(f"Adventurer with ID {adventurer_id} not found")

        try:
            current_experience = adventurer.experience
            current_level = adventurer.level
            adventurer.experience += experience_gain  # type: ignore

            required_exp = self.level_calculator.calculate_req_exp(current_level)  # type: ignore

            leveled_up = False
            if current_experience + experience_gain >= required_exp:  # type: ignore

                adventurer.level += 1  # type: ignore
                adventurer.experience = 0  # type: ignore

                leveled_up = True
                adventurer.leveled_up = True  # type: ignore

            self.db.commit()

            if leveled_up:
                send_level_up_email.delay(
                    adventurer_id=str(adventurer.id), old_level=current_level, new_level=adventurer.level
                )

            return adventurer
        except (TypeError, ValueError) as e:
            self.db.rollback()
            raise AdventurerValidationError(f"Error gaining experience: {str(e)}") from e

    def adventurer_to_dict(self, adventurer: Adventurer) -> Dict[str, Any]:
        """
        Convert an adventurer to a dictionary for JSON serialization.

        Args:
            adventurer: The adventurer to convert

        Returns:
            Dict[str, Any]: A dictionary representation of the adventurer
        """
        # experience_for_next_level = self.level_calculator.calculate_req_exp(adventurer.level)  # type: ignore

        # progress_percentage = (
        #     (adventurer.experience / experience_for_next_level * 100) if experience_for_next_level > 0 else 100
        # )

        # completed_quests = [
        #     completion.quest_id
        #     for completion in self.db.query(QuestCompletion).filter_by(adventurer_id=adventurer.id).all()
        # ]

        return {
            "id": adventurer.id,
            "name": adventurer.name,
            "level": adventurer.level,
            "adventurer_type": adventurer.adventurer_type,
            "experience": adventurer.experience,
            # "experience_for_next_level": experience_for_next_level,
            # "progress_percentage": round(progress_percentage, 2),  # type: ignore
            "created_at": adventurer.created_at,
            "updated_at": adventurer.updated_at,
            # "completed_quests_count": len(completed_quests),
            # "completed_quests": completed_quests,
        }
