import random

import pytest

from src.side_quest_py.models.adventurer import (
    Adventurer,
    AdventurerExperienceError,
    AdventurerLevelError,
    AdventurerQuestError,
    AdventurerValidationError,
    LevelCalculator,
)
from src.side_quest_py.models.user import User


@pytest.fixture
def calculator() -> LevelCalculator:
    """Return a fresh instance of LevelCalculator"""
    return LevelCalculator()


@pytest.fixture
def adventurer() -> Adventurer:
    """Returns a test adventurer record"""
    test_names = ["Aragorn", "Frodo", "Gandalf", "Scarlett", "Bob"]
    random_index = random.randrange(len(test_names))
    name = test_names[random_index]
    return Adventurer(name=name, user_id="test_user_id")


@pytest.fixture
def user() -> User:
    """Returns a test user record"""
    return User(id="test_user_id", username="test_user", email="test_user@example.com")


class TestAdventurer:
    def test_adventurer_creation(self, adventurer: Adventurer) -> None:
        """Test the creation of an Adventurer with valid parameters"""
        # Arrange & Act are handled by the fixture

        # Assert
        assert adventurer.level == 1
        assert adventurer.experience == 0
        assert len(adventurer.completed_quests) == 0

    def test_adventurer_creation_with_invalid_name(self) -> None:
        """Test that creating an adventurer with an invalid name raises AdventurerValidationError"""
        # Arrange
        name = ""

        # Act
        with pytest.raises(AdventurerValidationError) as exc_info:
            _ = Adventurer(name=name, user_id="test_user_id")

        # Assert
        assert "Adventurer name cannot be empty" in str(exc_info.value)

    def test_adventurer_creation_with_negative_level(self) -> None:
        """Test that creating an adventurer with negative level raises AdventurerValidationError"""
        # Arrange
        name = "Test"

        # Act
        with pytest.raises(AdventurerLevelError) as exc_info:
            _ = Adventurer(name=name, user_id="test_user_id", level=-1)

        # Assert
        assert "Level must be a positive integer" in str(exc_info.value)


class TestLevelCalculator:
    def test_calculate_req_exp(self, calculator: LevelCalculator) -> None:
        """Test that the required experience is calculated correctly based on level"""
        # Arrange and act are handled by fixture

        # Assert
        assert calculator.calculate_req_exp(1) == 100
        assert calculator.calculate_req_exp(5) == 500
        assert calculator.calculate_req_exp(8) == 800
        assert calculator.calculate_req_exp(10) == 1000

    def test_calculate_req_exp_invalid(self, calculator: LevelCalculator) -> None:
        """Test that an invalid level value raises AdventurerLevelError"""
        # Arrange is handled by fixture

        # Act
        with pytest.raises(AdventurerLevelError) as exc_info:
            calculator.calculate_req_exp(-1)

        # Assert
        assert "Level must be greater than 0" in str(exc_info.value)

    def test_calculate_req_exp_invalid_type(self, calculator: LevelCalculator) -> None:
        """Test that passing invalid type to calculate_req_exp raises AdventurerLevelError"""
        # Arrange is handled by fixture

        # Act & Assert
        with pytest.raises(AdventurerLevelError) as exc_info:
            calculator.calculate_req_exp("invalid")  # type: ignore
        assert "Invalid level type" in str(exc_info.value)

    def test_has_leveled_up(self, calculator: LevelCalculator) -> None:
        """Test that an adventurer has leveled up when required exp is obtained"""
        # Arrange & Act are handled by fixture

        # Assert
        assert calculator.has_leveled_up(1, 100) == True
        assert calculator.has_leveled_up(5, 500) == True
        assert calculator.has_leveled_up(1, 75) == False
        assert calculator.has_leveled_up(5, 400) == False

    def test_has_leveled_up_invalid_level(self, calculator: LevelCalculator) -> None:
        """Test that has_leveled_up raises AdventurerLevelError with invalid level"""
        # Arrange is handled by fixture

        # Act & Assert
        with pytest.raises(AdventurerLevelError) as exc_info:
            calculator.has_leveled_up(-1, 100)
        assert "Level must be greater than 0" in str(exc_info.value)

    def test_has_leveled_up_negative_experience(self, calculator: LevelCalculator) -> None:
        """Test that has_leveled_up raises AdventurerExperienceError with negative experience"""
        # Arrange is handled by fixture

        # Act & Assert
        with pytest.raises(AdventurerExperienceError) as exc_info:
            calculator.has_leveled_up(5, -100)
        assert "Experience cannot be negative" in str(exc_info.value)
