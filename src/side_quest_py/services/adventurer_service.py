from typing import Any, Dict, List, Optional

from ..models.adventurer import Adventurer, AdventurerValidationError


class AdventurerService:
    """Service for handling adventurer-related operations."""

    def __init__(self) -> None:
        """Initialize the adventurer service with an in-memory store."""
        self.adventurers: Dict[str, Adventurer] = {}

    def create_adventurer(
        self, name: str, level: int = 1, experience: int = 0
    ) -> Adventurer:
        """
        Create a new adventurer.

        Args:
            name: The name of the adventurer
            level: The starting level of the adventurer (default: 1)
            experience: The starting experience of the adventurer (default: 0)

        Returns:
            Adventurer: The newly created adventurer

        Raises:
            AdventurerValidationError: If the adventurer data is invalid
        """
        try:
            adventurer = Adventurer(name=name, _level=level, experience=experience)
            self.adventurers[name] = adventurer
            return adventurer
        except AdventurerValidationError as e:
            raise e
        except Exception as e:
            raise AdventurerValidationError(f"Error creating adventurer: {str(e)}")

    def get_adventurer(self, name: str) -> Optional[Adventurer]:
        """
        Get an adventurer by name.

        Args:
            name: The name of the adventurer

        Returns:
            Optional[Adventurer]: The adventurer if found, None otherwise
        """
        return self.adventurers.get(name)

    def get_all_adventurers(self) -> List[Adventurer]:
        """
        Get all adventurers.

        Returns:
            List[Adventurer]: A list of all adventurers
        """
        return list(self.adventurers.values())

    def delete_adventurer(self, name: str) -> bool:
        """
        Delete an adventurer by name.

        Args:
            name: The name of the adventurer

        Returns:
            bool: True if the adventurer was deleted, False otherwise
        """
        if name in self.adventurers:
            del self.adventurers[name]
            return True
        return False

    def adventurer_to_dict(self, adventurer: Adventurer) -> Dict[str, Any]:
        """
        Convert an adventurer to a dictionary for JSON serialization.

        Args:
            adventurer: The adventurer to convert

        Returns:
            Dict[str, Any]: A dictionary representation of the adventurer
        """
        return {
            "name": adventurer.name,
            "level": adventurer.level,
            "experience": adventurer.experience,
            "experience_for_next_level": adventurer.exp_for_next_level,
            "progress_percentage": round(adventurer.exp_progress_percentage, 2),
            "completed_quests_count": len(adventurer.completed_quests),
            "completed_quests": list(adventurer.completed_quests),
        }
