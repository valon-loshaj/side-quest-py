from typing import Dict, Any, Optional, List
from src.side_quest_py.models.quest import (
    Quest,
    QuestValidationError,
    QuestCompletionError,
    QuestNotFoundError,
    QuestServiceError,
)


class QuestService:
    """Service for handling quest-related operations."""

    def __init__(self):
        """Initialize the quest service with an in-memory store."""
        self.quests: Dict[str, Quest] = {}

    def create_quest(self, title: str) -> Quest:
        """
        Create a new quest.

        Args:
            title: The title of the quest
        """
        try:
            quest = Quest(title=title)
            # Store quest using its ULID string as the key
            self.quests[quest.id] = quest
            return quest
        except QuestValidationError as e:
            raise e
        except Exception as e:
            raise QuestValidationError(f"Error creating quest: {str(e)}")

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """
        Get a quest by its ID.

        Args:
            quest_id: The ULID string ID of the quest
        """
        try:
            return self.quests.get(quest_id)
        except Exception as e:
            raise QuestNotFoundError(f"Quest with ID: {quest_id} not found")

    def get_all_quests(self) -> List[Quest]:
        """
        Get all quests.
        """
        try:
            return list(self.quests.values())
        except Exception as e:
            raise QuestServiceError(f"Error getting all quests: {str(e)}")

    def complete_quest(self, quest_id: str) -> Quest:
        """
        Complete a quest.

        Args:
            quest_id: The ULID string ID of the quest
        """
        try:
            quest = self.get_quest(quest_id)
            if not quest:
                raise QuestNotFoundError(f"Quest with ID: {quest_id} not found")
            quest.complete()
            return quest
        except QuestCompletionError as e:
            raise e
        except Exception as e:
            raise QuestCompletionError(f"Error completing quest: {str(e)}")

    def quest_to_dict(self, quest: Quest) -> Dict[str, Any]:
        """
        Convert a quest to a dictionary.
        """
        return {"id": quest.id, "title": quest.title, "completed": quest.completed}
