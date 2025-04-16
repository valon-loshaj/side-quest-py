from typing import Any, Dict, List, Optional

from .. import db
from ..models.db_models import Quest
from ..models.quest import (
    QuestCompletionError,
    QuestNotFoundError,
    QuestServiceError,
    QuestValidationError,
)
from .quest_completion_service import QuestCompletionService
from ulid import ULID


class QuestService:
    """Service for handling quest-related operations."""

    def create_quest(self, title: str, adventurer_id: str, experience_reward: int = 100) -> Quest:
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
            # Validate input
            if not title or not title.strip():
                raise QuestValidationError("Quest title cannot be empty")
            if experience_reward < 0:
                raise QuestValidationError("Experience reward cannot be negative")
            if not adventurer_id:
                raise QuestValidationError("Adventurer ID is required")

            # Create new quest with a generated ID
            quest = Quest(
                id=str(ULID()),
                title=title,
                experience_reward=experience_reward,
                completed=False,
                adventurer_id=adventurer_id,
            )

            # Add to database
            db.session.add(quest)
            db.session.commit()

            return quest
        except QuestValidationError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise QuestValidationError(f"Error creating quest: {str(e)}") from e

    def get_quest(self, quest_id: str) -> Optional[Quest]:
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
            quest: Optional[Quest] = Quest.query.get(quest_id)
            return quest
        except Exception as e:
            raise QuestNotFoundError(f"Quest with ID: {quest_id} not found") from e

    def get_all_quests(self, adventurer_id: str) -> List[Quest]:
        """
        Get all quests.

        Returns:
            List[Quest]: A list of all quests

        Raises:
            QuestServiceError: If there's an error getting all quests
        """
        try:
            quests: List[Quest] = Quest.query.filter_by(adventurer_id=adventurer_id).all()
            return quests
        except Exception as e:
            raise QuestServiceError(f"Error getting all quests: {str(e)}") from e

    def get_uncompleted_quests(self) -> List[Quest]:
        """
        Get all uncompleted quests.

        Returns:
            List[Quest]: A list of all uncompleted quests

        Raises:
            QuestServiceError: If there's an error getting the quests
        """
        try:
            quests: List[Quest] = Quest.query.filter_by(completed=False).all()
            return quests
        except Exception as e:
            raise QuestServiceError(f"Error getting uncompleted quests: {str(e)}") from e

    def update_quest(
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
            quest = self.get_quest(quest_id)
            if not quest:
                raise QuestNotFoundError(f"Quest with ID: {quest_id} not found")

            # Save previous completion status
            was_previously_completed = quest.completed

            # Update fields only if they are provided
            if title is not None:
                setattr(quest, "title", title)

            if adventurer_id is not None:
                setattr(quest, "adventurer_id", adventurer_id)

            if experience_reward is not None:
                setattr(quest, "experience_reward", experience_reward)

            if completed is not None:
                # Check if quest is being marked as incomplete after being completed
                if was_previously_completed is True and completed is False:
                    quest_completion_service = QuestCompletionService()
                    quest_completion_service.delete_quest_completion(quest_id)
                setattr(quest, "completed", completed)

            db.session.commit()

            return quest
        except (QuestNotFoundError, QuestCompletionError) as e:
            db.session.rollback()
            raise e
        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise QuestCompletionError(f"Error completing quest: {str(e)}") from e

    def delete_quest(self, quest_id: str) -> bool:
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
            quest = self.get_quest(quest_id)
            if not quest:
                raise QuestNotFoundError(f"Quest with ID: {quest_id} not found")

            db.session.delete(quest)
            db.session.commit()

            return True
        except QuestNotFoundError as e:
            raise e
        except Exception as e:
            db.session.rollback()
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
            "title": quest.title,
            "experience_reward": quest.experience_reward,
            "completed": quest.completed,
            "adventurer_id": quest.adventurer_id,
        }
