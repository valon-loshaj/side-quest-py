import pytest

from src.side_quest_py.models.quest import (
    Quest,
    QuestCompletionError,
    QuestValidationError,
)


def test_quest_creation():
    """Test basic quest creation with valid data."""
    quest = Quest(title="Test Quest")
    assert quest.title == "Test Quest"
    assert quest.experience_reward == 50  # Default value
    assert not quest.completed
    assert quest.id is not None
    assert len(quest.id) > 0


def test_quest_creation_with_custom_experience():
    """Test quest creation with custom experience reward."""
    quest = Quest(title="Test Quest", experience_reward=100)
    assert quest.experience_reward == 100


def test_quest_validation_empty_title():
    """Test that creating a quest with empty title raises error."""
    with pytest.raises(QuestValidationError) as exc_info:
        Quest(title="")
    assert "Quest title cannot be empty" in str(exc_info.value)


def test_quest_validation_whitespace_title():
    """Test that creating a quest with whitespace-only title raises error."""
    with pytest.raises(QuestValidationError) as exc_info:
        Quest(title="   ")
    assert "Quest title cannot be empty" in str(exc_info.value)


def test_quest_validation_negative_experience():
    """Test that creating a quest with negative experience raises error."""
    with pytest.raises(QuestValidationError) as exc_info:
        Quest(title="Test Quest", experience_reward=-10)
    assert "Experience reward cannot be negative" in str(exc_info.value)


def test_quest_completion():
    """Test quest completion functionality."""
    quest = Quest(title="Test Quest")
    assert not quest.completed
    quest.complete()
    assert quest.completed


def test_quest_double_completion():
    """Test that completing an already completed quest raises error."""
    quest = Quest(title="Test Quest")
    quest.complete()
    with pytest.raises(QuestCompletionError) as exc_info:
        quest.complete()
    assert "Quest is already completed" in str(exc_info.value)


def test_quest_string_representation():
    """Test the string representation of a quest."""
    quest = Quest(title="Test Quest")
    quest_str = str(quest)
    assert "Test Quest" in quest_str
    assert quest.id in quest_str


def test_quest_is_completed_property():
    """Test the is_completed property."""
    quest = Quest(title="Test Quest")
    assert not quest.is_completed
    quest.complete()
    assert quest.is_completed


def test_quest_unique_ids():
    """Test that each quest gets a unique ID."""
    quest1 = Quest(title="Quest 1")
    quest2 = Quest(title="Quest 2")
    assert quest1.id != quest2.id
