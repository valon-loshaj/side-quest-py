from .. import db
from ..models.db_models import QuestCompletion
from ..models.quest import QuestCompletionError, QuestNotFoundError


class QuestCompletionService:
    """Service for handling quest completion-related operations."""

    def create_quest_completion(self, quest_id: str, adventurer_id: str) -> QuestCompletion:
        """
        Create a new quest completion record.

        Args:
            quest_id: The ID of the quest
            adventurer_id: The ID of the adventurer

        Returns:
            QuestCompletion: The new quest completion record

        Raises:
            QuestNotFoundError: If the quest is not found
            QuestCompletionError: If there's an error creating the quest completion
        """
        try:
            quest_completion = QuestCompletion(
                quest_id=quest_id,
                adventurer_id=adventurer_id,
            )
            db.session.add(quest_completion)
            db.session.commit()
            return quest_completion
        except QuestNotFoundError as e:
            db.session.rollback()
            raise e
        except QuestCompletionError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise QuestCompletionError(f"Error creating quest completion: {str(e)}") from e

    def get_quest_completion(self, quest_id: str) -> QuestCompletion:
        """
        Get a quest completion record by quest ID.

        Args:
            quest_id: The ID of the quest

        Returns:
            QuestCompletion: The quest completion record

        Raises:
            QuestCompletionError: If there's an error getting the quest completion
        """
        try:
            quest_completion = QuestCompletion.query.filter_by(quest_id=quest_id).first()
            return quest_completion
        except QuestCompletionError as e:
            db.session.rollback()
            raise e
        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise QuestCompletionError(f"Error getting quest completion: {str(e)}") from e

    def delete_quest_completion(self, quest_id: str) -> bool:
        """
        Delete a quest completion record by quest ID.

        Args:
            quest_id: The ID of the quest

        Returns:
            bool: True if the quest completion was deleted, False otherwise

        Raises:
            QuestCompletionError: If there's an error deleting the quest completion
        """
        try:
            quest_completion = QuestCompletion.query.filter_by(quest_id=quest_id).first()
            db.session.delete(quest_completion)
            db.session.commit()
            return True
        except QuestCompletionError as e:
            db.session.rollback()
            raise e
        except (TypeError, ValueError) as e:
            db.session.rollback()
            raise QuestCompletionError(f"Error deleting quest completion: {str(e)}") from e
