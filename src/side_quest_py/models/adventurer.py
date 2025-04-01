from dataclasses import dataclass, field
from typing import Set, Tuple

class LevelCalculator:
    """handles the logic necessary when an adventurer levels up"""
    def calculate_req_exp(self, level: int) -> int:
        """
        calculate the experience needed to reach the next level

        args:
            level (int): the next level we are trying to calculate the req experience to reach

        raises:
            ValueError: if the level is less than 1

        returns:
            int: the amount of experience required to reach that level
        """
        if level < 1:
            raise ValueError("Level must be greater than 0")
        
        return level * 100
    
    def has_leveled_up(self, level: int, experience_gain: int) -> bool:
        """
        checks if an adventurer has leveled up

        Args:
            level (int): the current level of the adventurer
            experience_gain (int): the experience gained by the adventurer

        Raises:
            ValueError: if the current level is less than 1 or if the experience gained is negative

        Returns:
            bool: whether the adventurer has leveled up
        """
        if level < 1:
            raise ValueError("Level must be greater than 0")
        if experience_gain < 0:
            raise ValueError("Experience cannot be negative")
        
        required_exp = self.calculate_req_exp(level)
        return experience_gain >= required_exp

@dataclass
class Adventurer:
    """
    this is an adventurer, they go on quests and gain experience!
    """
    name: str
    _level: int = field(default=1)
    experience: int = 0
    completed_quests: Set[str] = field(default_factory=set)
    level_calculator: LevelCalculator = field(default_factory=LevelCalculator)
    
    def __post_init__(self) -> None:
        """Validate the initial values when an adventurer is created."""
        if not self.name:
            raise ValueError("Adventurer must have a name")
        if self.level < 1:
            raise ValueError("Adventurer level cannot be a negative number or 0")
        if self.experience < 0:
            raise ValueError("Adventurer cannot have negative experience")
    
    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the adventurer.
        
        This is called when you use print(adventurer) or str(adventurer).
        """
        quest_count = len(self.completed_quests)
        return f"{self.name} (Level {self.level}) - {self.experience} XP, {quest_count} quests completed"
    
    
        
    @property
    def level(self) -> int:
        """
        getter property for the current level of the adventurer

        Returns:
            int: adventurer current level
        """
        return self._level
    
    @property
    def exp_for_next_level(self) -> int:
        """
        getter property for the exp required for the next level

        Returns:
            int: exp required for next level
        """
        return self.level_calculator.calculate_req_exp(self.level)
    
    @property
    def exp_progress_percentage(self) -> float:
        """
        getter property for the progress towards the next level
        
        Returns:
            float: percentage progress towards next level (0 - 100)
        """
        required_exp = self.exp_for_next_level
        return (self.experience / required_exp) * 100 if required_exp > 0 else 100
            
    def complete_quest(self, quest_id: str, experience_gain: int) -> Tuple[bool, bool]:
        """
        when an adventurer completes a quest:
        1) add the quest with id equal to quest_id to the completed quests
        2) add the experience_gain to the adventurers total experience
        
        args:
        - quest_id: unique id for the quest that was completed
        - experience_gain: amount of experience earned by completing this quest
        
        returns:
        a tuple of [was_new_completion, leveled_up]
        - was_new_completion: bool that signals this quest was a newly completed quest
        - leveled_up: whether bool that signals a level up occurred
        
        raises:
        - ValueError: when the quest_id is empty or the experience_gain is negative
        """
        if not quest_id:
            raise ValueError("Quest ID cannot be empty")
        if experience_gain < 0:
            raise ValueError("Experience gain cannot be negative")
        
        was_new = quest_id not in self.completed_quests
        self.completed_quests.add(quest_id)
        
        leveled_up = False
        if was_new:
            leveled_up = self.gain_experience(experience_gain)
            
        return (was_new, leveled_up)
            
    def gain_experience(self, experience_gain) -> bool:
        """
        add the experience gained to the adventurer and determine if is resulted in a level up
        
        args:
        - experience_gain: amount of experience gained by adventurer
        
        returns:
            true if a level up occured
            false if no level up occured
            
        raises:
        - ValueError if the experience gained is negative
        """
        if experience_gain < 0:
            raise ValueError("Experience gain cannot be negative")
        
        self.experience += experience_gain
        leveled_up = self._check_level_up()
        if leveled_up:
            self.experience = 0
        
        return leveled_up
    
    def get_exp_for_next_level(self, level: int) -> int:
        """
        calculates the total exp required to reach the next level

        Args:
            level (int): the current level of the adventurer

        Returns:
            int: the amount of experience required to reach the next level
        """
        return self.level_calculator.calculate_req_exp(level)
    
    def get_exp_progress(self) -> Tuple[int, int, float]:
        """
        get details of current exp progress

        Returns:
            Tuple[int, int, float]: 
            - current exp
            - exp required for next level
            - percentage to next level
        """
        required_exp = self.get_exp_for_next_level(self.level)
        progress = (self.experience / required_exp) * 100 if required_exp > 0 else 100
        return (self.experience, required_exp, progress)
    
    def _check_level_up(self) -> bool:
        """
        check if adventurer has enough experience to level up

        returns:
            bool: whether the adventurer leveled up
        """
        if self.level_calculator.has_leveled_up(self.level, self.experience):
            self._level += 1
            return True
        return False
        