"""
This module contains the service for handling quest-related operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session
from ulid import ULID

from src.side_quest_py.database import get_db
from src.side_quest_py.models.db_models import Quest, Adventurer
from src.side_quest_py.models.quest import (
    QuestCompletionError,
    QuestNotFoundError,
    QuestServiceError,
    QuestValidationError,
)
from .quest_completion_service import QuestCompletionService
from .adventurer_service import AdventurerService


class QuestService:
    """Service for handling quest-related operations."""

    def __init__(self, db: Session = Depends(get_db)) -> None:
        """Initialize the quest service."""
        self.db = db

    async def create_quest(self, title: str, adventurer_id: str, experience_reward: int = 100) -> Quest:
        """
        Create a new quest.

        Args:
            title: The title of the quest
            adventurer_id: The ID of the adventurer who is assigned the quest
            experience_reward: The experience reward for completing the quest

        Returns:
            Quest: The newly created quest

        Raises:
            QuestValidationError: If the quest data is invalid
        """
        try:
            if not title or not title.strip():
                raise QuestValidationError("Quest title cannot be empty")
            if experience_reward < 0:
                raise QuestValidationError("Experience reward cannot be negative")
            if not adventurer_id:
                raise QuestValidationError("Adventurer ID is required")

            adventurer = self.db.query(Adventurer).filter_by(id=adventurer_id).first()
            if not adventurer:
                raise QuestValidationError(f"Adventurer with ID {adventurer_id} does not exist")

            quest = Quest(
                id=str(ULID()),
                title=title,
                experience_reward=experience_reward,
                completed=False,
                adventurer_id=adventurer_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.db.add(quest)
            self.db.commit()

            return quest
        except QuestValidationError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise QuestValidationError(f"Error creating quest: {str(e)}") from e

    async def get_quest(self, quest_id: str) -> Optional[Quest]:
        """
        Get a quest by its ID.

        Args:
            quest_id: The string ID of the quest

        Returns:
            Optional[Quest]: The quest if found, None otherwise

        Raises:
            QuestNotFoundError: If there's an error finding the quest
        """
        try:
            quest: Optional[Quest] = self.db.query(Quest).filter_by(id=quest_id).first()
            return quest
        except Exception as e:
            raise QuestNotFoundError(f"Quest with ID: {quest_id} not found") from e

    async def get_all_quests(self, adventurer_id: str) -> List[Quest]:
        """
        Get all quests.

        Returns:
            List[Quest]: A list of all quests

        Raises:
            QuestServiceError: If there's an error getting all quests
        """
        try:
            quests: List[Quest] = self.db.query(Quest).filter_by(adventurer_id=adventurer_id).all()
            return quests
        except Exception as e:
            raise QuestServiceError(f"Error getting all quests: {str(e)}") from e

    async def get_uncompleted_quests(self) -> List[Quest]:
        """
        Get all uncompleted quests.

        Returns:
            List[Quest]: A list of all uncompleted quests

        Raises:
            QuestServiceError: If there's an error getting the quests
        """
        try:
            quests: List[Quest] = self.db.query(Quest).filter_by(completed=False).all()
            return quests
        except Exception as e:
            raise QuestServiceError(f"Error getting uncompleted quests: {str(e)}") from e

    async def update_quest(
        self,
        quest_id: str,
        title: Optional[str] = None,
        adventurer_id: Optional[str] = None,
        experience_reward: Optional[int] = None,
        completed: Optional[bool] = None,
    ) -> Quest:
        """
        Update a quest with partial data.

        Args:
            quest_id: The string ID of the quest
            title: Optional - The title of the quest
            adventurer_id: Optional - The ID of the adventurer who is assigned the quest
            experience_reward: Optional - The experience reward for completing the quest
            completed: Optional - Whether the quest has been completed

        Returns:
            Quest: The updated quest

        Raises:
            QuestNotFoundError: If the quest is not found
            QuestCompletionError: If there's an error completing the quest
        """
        try:
            quest = await self.get_quest(quest_id)
            if not quest:
                raise QuestNotFoundError(f"Quest with ID: {quest_id} not found")

            was_previously_completed = quest.completed

            if title is not None:
                setattr(quest, "title", title)

            if adventurer_id is not None:
                setattr(quest, "adventurer_id", adventurer_id)

            if experience_reward is not None:
                setattr(quest, "experience_reward", experience_reward)

            if completed is not None:
                if was_previously_completed is True and completed is False:
                    quest_completion_service = QuestCompletionService(db=self.db)
                    quest_completion_service.delete_quest_completion(quest_id)
                setattr(quest, "completed", completed)
                if completed is True:
                    adventurer_id_str = str(adventurer_id) if adventurer_id is not None else str(quest.adventurer_id)
                    experience_reward_int = (
                        experience_reward if experience_reward is not None else quest.experience_reward
                    )
                    quest_completion_service = QuestCompletionService(db=self.db)
                    quest_completion_service.create_quest_completion(quest_id, adventurer_id_str)
                    adventurer_service = AdventurerService(db=self.db)
                    await adventurer_service.gain_experience(adventurer_id_str, experience_reward_int)  # type: ignore
                    setattr(quest, "completed", True)

            self.db.commit()

            return quest
        except (QuestNotFoundError, QuestCompletionError) as e:
            self.db.rollback()
            raise e
        except (TypeError, ValueError) as e:
            self.db.rollback()
            raise QuestCompletionError(f"Error completing quest: {str(e)}") from e

    async def delete_quest(self, quest_id: str) -> bool:
        """
        Delete a quest by ID.

        Args:
            quest_id: The string ID of the quest

        Returns:
            bool: True if the quest was deleted

        Raises:
            QuestNotFoundError: If the quest is not found
            QuestServiceError: If there's an error deleting the quest
        """
        try:
            quest = await self.get_quest(quest_id)
            if not quest:
                raise QuestNotFoundError(f"Quest with ID: {quest_id} not found")

            self.db.delete(quest)
            self.db.commit()

            return True
        except QuestNotFoundError as e:
            raise e
        except Exception as e:
            self.db.rollback()
            raise QuestServiceError(f"Error deleting quest: {str(e)}") from e

    def quest_to_dict(self, quest: Quest) -> Dict[str, Any]:
        """
        Convert a quest to a dictionary.

        Args:
            quest: The quest to convert

        Returns:
            Dict[str, Any]: A dictionary representation of the quest
        """
        return {
            "id": quest.id,
            "adventurer_id": quest.adventurer_id,
            "title": quest.title,
            "experience_reward": quest.experience_reward,
            "completed": quest.completed,
            "created_at": quest.created_at,
            "updated_at": quest.updated_at,
        }
