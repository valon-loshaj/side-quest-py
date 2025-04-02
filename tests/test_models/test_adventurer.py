import pytest
import random
from src.side_quest_py.models.adventurer import (
    Adventurer, 
    LevelCalculator,
    AdventurerValidationError,
    AdventurerExperienceError,
    AdventurerLevelError,
    AdventurerQuestError
)

@pytest.fixture
def level_calculator():
    """Return a fresh instance of LevelCalculator"""
    return LevelCalculator()

@pytest.fixture
def test_adventurer():
    """Returns a test adventurer record"""
    test_names = ["Aragorn", "Frodo", "Gandalf", "Scarlett", "Bob"]
    random_index = random.randrange(len(test_names))
    name = test_names[random_index]
    return Adventurer(name)

class TestAdventurer:
    def test_adventurer_creation(self, test_adventurer):
        """Test the creation of an Adventurer with valid parameters"""
        # Arrange & Act are handled by the fixture
        
        # Assert
        assert test_adventurer.level == 1
        assert test_adventurer.experience == 0
        assert len(test_adventurer.completed_quests) == 0
        
    def test_adventurer_creation_with_invalid_name(self):
        """Test that creating an adventurer with an invalid name raises AdventurerValidationError"""
        # Arrange
        name = ""
        
        # Act
        with pytest.raises(AdventurerValidationError) as exc_info:
            adventurer = Adventurer(name)
        
        # Assert
        assert str(exc_info.value) == "Adventurer must have a name"
        
    def test_adventurer_creation_with_negative_level(self):
        """Test that creating an adventurer with negative level raises AdventurerValidationError"""
        # Arrange
        name = "Test"
        
        # Act
        with pytest.raises(AdventurerValidationError) as exc_info:
            adventurer = Adventurer(name, _level=-1)
        
        # Assert
        assert "Adventurer level cannot be a negative number or 0" in str(exc_info.value)
        
    def test_adventurer_creation_with_negative_experience(self):
        """Test that creating an adventurer with negative experience raises AdventurerValidationError"""
        # Arrange
        name = "Test"
        
        # Act
        with pytest.raises(AdventurerValidationError) as exc_info:
            adventurer = Adventurer(name, experience=-10)
        
        # Assert
        assert "Adventurer cannot have negative experience" in str(exc_info.value)
        
    def test_gain_experience(self):
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
        
    def test_gain_negative_experience(self):
        """Test that gaining negative experience raises AdventurerExperienceError"""
        # Arrange
        adventurer = Adventurer("Gandalf")
        
        # Act & Assert
        with pytest.raises(AdventurerExperienceError) as exc_info:
            adventurer.gain_experience(-10)
        assert "Experience gain cannot be negative" in str(exc_info.value)
        
    def test_level_up(self):
        """Test that when experience gain results in a level up, the adventurer increases in level by 1"""
        # Arrange
        adventurer = Adventurer("Scarlett")
        
        # Act
        adventurer.gain_experience(100)
        
        # Assert
        assert adventurer.experience == 0
        assert adventurer.level == 2
        assert adventurer.has_leveled_up()  # Should be True after level up
        
    def test_complete_quest(self):
        """Test the completion of a quest"""
        # Arrange
        adventurer = Adventurer("Frodo")
        quest_id = "quest_001"
        experience_gain = 25
        initial_exp = adventurer.experience
        
        # Act
        was_new, leveled_up = adventurer.complete_quest(quest_id, experience_gain)
        
        # Assert
        assert was_new == True
        assert leveled_up == False
        assert len(adventurer.completed_quests) == 1
        assert quest_id in adventurer.completed_quests
        assert adventurer.experience == initial_exp + experience_gain
        
    def test_complete_quest_with_empty_id(self):
        """Test that completing a quest with empty ID raises AdventurerQuestError"""
        # Arrange
        adventurer = Adventurer("Frodo")
        quest_id = ""
        experience_gain = 25
        
        # Act & Assert
        with pytest.raises(AdventurerQuestError) as exc_info:
            adventurer.complete_quest(quest_id, experience_gain)
        assert "Quest ID cannot be empty" in str(exc_info.value)
        
    def test_complete_quest_with_negative_experience(self):
        """Test that completing a quest with negative experience raises AdventurerQuestError"""
        # Arrange
        adventurer = Adventurer("Frodo")
        quest_id = "quest_001"
        experience_gain = -25
        
        # Act & Assert
        with pytest.raises(AdventurerQuestError) as exc_info:
            adventurer.complete_quest(quest_id, experience_gain)
        assert "Experience gain cannot be negative" in str(exc_info.value)
        
    def test_complete_quest_twice(self):
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
        assert was_new == False
        assert leveled_up == False
        assert len(adventurer.completed_quests) == 1
        assert quest_id in adventurer.completed_quests
        assert adventurer.experience == initial_exp + experience_gain
        
    def test_has_leveled_up(self):
        """Test the has_leveled_up method correctly reports level up status"""
        # Arrange
        adventurer = Adventurer("Aragorn")
        
        # Act & Assert
        assert not adventurer.has_leveled_up()
        
        adventurer.gain_experience(100)
        assert adventurer.has_leveled_up()
        
        adventurer.gain_experience(50)
        assert adventurer.has_leveled_up()
        
        was_new, leveled_up = adventurer.complete_quest("quest_001", 50)
        assert not leveled_up
        assert not adventurer.has_leveled_up()
        
        was_new, leveled_up = adventurer.complete_quest("quest_002", 100)
        assert leveled_up
        assert adventurer.has_leveled_up()

class TestLevelCalculator:
    def test_calculate_req_exp(self, level_calculator):
        """Test that the required experience is calculated correctly based on level"""
        # Arrange and act are handled by fixture
        
        # Assert
        assert level_calculator.calculate_req_exp(1) == 100
        assert level_calculator.calculate_req_exp(5) == 500
        assert level_calculator.calculate_req_exp(8) == 800
        assert level_calculator.calculate_req_exp(10) == 1000
        
    def test_calculate_req_exp_invalid(self, level_calculator):
        """Test that an invalid level value raises AdventurerLevelError"""
        # Arrange is handled by fixture
        
        # Act
        with pytest.raises(AdventurerLevelError) as exc_info:
            level_calculator.calculate_req_exp(-1)
        
        # Assert
        assert "Level must be greater than 0" in str(exc_info.value)
        
    def test_calculate_req_exp_invalid_type(self, level_calculator):
        """Test that passing invalid type to calculate_req_exp raises AdventurerLevelError"""
        # Arrange is handled by fixture
        
        # Act & Assert
        with pytest.raises(AdventurerLevelError) as exc_info:
            level_calculator.calculate_req_exp("invalid")
        assert "Invalid level type" in str(exc_info.value)
        
    def test_has_leveled_up(self, level_calculator):
        """Test that an adventurer has leveled up when required exp is obtained"""
        # Arrange & Act are handled by fixture
        
        # Assert
        assert level_calculator.has_leveled_up(1, 100) == True
        assert level_calculator.has_leveled_up(5, 500) == True
        assert level_calculator.has_leveled_up(1, 75) == False
        assert level_calculator.has_leveled_up(5, 400) == False
        
    def test_has_leveled_up_invalid_level(self, level_calculator):
        """Test that has_leveled_up raises AdventurerLevelError with invalid level"""
        # Arrange is handled by fixture
        
        # Act & Assert
        with pytest.raises(AdventurerLevelError) as exc_info:
            level_calculator.has_leveled_up(-1, 100)
        assert "Level must be greater than 0" in str(exc_info.value)
        
    def test_has_leveled_up_negative_experience(self, level_calculator):
        """Test that has_leveled_up raises AdventurerExperienceError with negative experience"""
        # Arrange is handled by fixture
        
        # Act & Assert
        with pytest.raises(AdventurerExperienceError) as exc_info:
            level_calculator.has_leveled_up(1, -100)
        assert "Experience cannot be negative" in str(exc_info.value)