from dataclasses import dataclass, field
from datetime import datetime

from ulid import ULID


class QuestCompletionError(Exception):
    """Raised when a quest completion fails validation."""


@dataclass
class QuestCompletion:
    """
    A quest completion is a record of a quest that has been completed by an adventurer.
    """

    adventurer_id: str
    quest_id: str
    id: str = field(default_factory=lambda: str(ULID()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """
        Validate the initial values when a quest completion is created.
        """
        self._validate_adventurer_id()
        self._validate_quest_id()

    def _validate_adventurer_id(self) -> None:
        """Validate the adventurer ID."""
        if not self.adventurer_id or not self.adventurer_id.strip():
            raise QuestCompletionError("Adventurer ID cannot be empty")

    def _validate_quest_id(self) -> None:
        """Validate the quest ID."""
        if not self.quest_id or not self.quest_id.strip():
            raise QuestCompletionError("Quest ID cannot be empty")
