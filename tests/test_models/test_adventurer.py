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

    def test_adventurer_creation_with_negative_experience(self) -> None:
        """Test that creating an adventurer with negative experience raises AdventurerValidationError"""
        # Arrange
        name = "Test"

        # Act
        with pytest.raises(AdventurerExperienceError) as exc_info:
            _ = Adventurer(name=name, user_id="test_user_id", experience=-10)

        # Assert
        assert "Experience must be a non-negative integer" in str(exc_info.value)

    def test_gain_experience(self) -> None:
        """Test that a gain of experience is added to the adventurer's total exp"""
        # Arrange
        adventurer = Adventurer("Gandalf")
        initial_experience = adventurer.experience

        # Act
        adventurer.gain_experience(50)

        # Assert
        assert adventurer.level == 1
        assert adventurer.experience == initial_experience + 50
        assert not adventurer.has_leveled_up()

    def test_gain_negative_experience(self) -> None:
        """Test that gaining negative experience raises AdventurerExperienceError"""
        # Arrange
        adventurer = Adventurer("Gandalf")

        # Act & Assert
        with pytest.raises(AdventurerExperienceError) as exc_info:
            adventurer.gain_experience(-10)
        assert "Experience gain cannot be negative" in str(exc_info.value)

    def test_level_up(self) -> None:
        """Test that when experience gain results in a level up, the adventurer increases in level by 1"""
        # Arrange
        adventurer = Adventurer("Scarlett")

        # Act
        adventurer.gain_experience(100)

        # Assert
        assert adventurer.experience == 0
        assert adventurer.level == 2
        assert adventurer.has_leveled_up()  # Should be True after level up

    def test_complete_quest(self) -> None:
        """Test the completion of a quest"""
        # Arrange
        adventurer = Adventurer("Frodo")
        quest_id = "quest_001"
        experience_gain = 25
        initial_exp = adventurer.experience

        # Act
        was_new, leveled_up = adventurer.complete_quest(quest_id, experience_gain)

        # Assert
        assert was_new is True
        assert leveled_up is False
        assert len(adventurer.completed_quests) == 1
        assert quest_id in adventurer.completed_quests
        assert adventurer.experience == initial_exp + experience_gain

    def test_complete_quest_with_empty_id(self) -> None:
        """Test that completing a quest with empty ID raises AdventurerQuestError"""
        # Arrange
        adventurer = Adventurer("Frodo")
        quest_id = ""
        experience_gain = 25

        # Act & Assert
        with pytest.raises(AdventurerQuestError) as exc_info:
            adventurer.complete_quest(quest_id, experience_gain)
        assert "Quest ID cannot be empty" in str(exc_info.value)

    def test_complete_quest_with_negative_experience(self) -> None:
        """Test that completing a quest with negative experience raises AdventurerQuestError"""
        # Arrange
        adventurer = Adventurer("Frodo")
        quest_id = "quest_001"
        experience_gain = -25

        # Act & Assert
        with pytest.raises(AdventurerQuestError) as exc_info:
            adventurer.complete_quest(quest_id, experience_gain)
        assert "Experience gain cannot be negative" in str(exc_info.value)

    def test_complete_quest_twice(self) -> None:
        """Test the completion of the same quest twice doesn't increase experience"""
        # Arrange
        adventurer = Adventurer("Bob")
        quest_id = "quest_001"
        experience_gain = 50
        initial_exp = adventurer.experience

        # Act
        adventurer.complete_quest(quest_id, experience_gain)
        was_new, leveled_up = adventurer.complete_quest(quest_id, experience_gain)

        # Assert
        assert was_new is False
        assert leveled_up is False
        assert len(adventurer.completed_quests) == 1
        assert quest_id in adventurer.completed_quests
        assert adventurer.experience == initial_exp + experience_gain

    def test_has_leveled_up(self) -> None:
        """Test the has_leveled_up method correctly reports level up status"""
        # Arrange
        adventurer = Adventurer("Aragorn")

        # Act & Assert
        assert not adventurer.has_leveled_up()

        adventurer.gain_experience(100)
        assert adventurer.has_leveled_up()

        adventurer._reset_level_up_status()

        adventurer.gain_experience(50)

        assert not adventurer.has_leveled_up()

        # Complete a quest that doesn't give enough exp to level up
        was_new, leveled_up = adventurer.complete_quest("quest_001", 50)
        assert was_new is True
        assert leveled_up is False

        # Complete a quest that gives enough exp to level up (level 2 requires 200 exp)
        was_new, leveled_up = adventurer.complete_quest("quest_002", 200)
        assert was_new is True
        assert leveled_up is True


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
