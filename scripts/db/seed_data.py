"""Functions for generating seed data for the database."""
import uuid
import random
from typing import Dict, List, Tuple
import bcrypt

from src.side_quest_py.models.db_models import User, Adventurer, Quest, QuestCompletion


def generate_user() -> User:
    """Generate a single admin user with password 'side_quest_user'.
    
    Returns:
        User: A User object with admin credentials
    """
    user = User(
        id=str(uuid.uuid4()),
        username="admin",
        email="admin@side-quest.com",
        password_hash=_hash_password("side_quest_user"),
        created_at=None,  # Use default
        updated_at=None,  # Use default
    )
    return user


def generate_adventurers(count: int, user_id: str) -> List[Adventurer]:
    """Generate a list of RPG-themed adventurers.
    
    Args:
        count: Number of adventurers to generate
        user_id: ID of the user these adventurers belong to
        
    Returns:
        List[Adventurer]: A list of Adventurer objects
    """
    rpg_names = [
        "Thorin Oakenshield",
        "Lyra Stormborn",
        "Grimlock the Mighty",
        "Elowen Moonshadow",
        "Garrick Fireheart",
        "Seraphina Wildheart",
        "Zephyr Ironhide",
        "Freya Dawnbreaker",
        "Branwen Nightshade",
        "Thalos Emberclaw"
    ]
    
    adventurers = []
    for i in range(min(count, len(rpg_names))):
        level = random.randint(1, 10)
        experience = level * random.randint(100, 500)
        
        adventurer = Adventurer(
            id=str(uuid.uuid4()),
            name=rpg_names[i],
            level=level,
            experience=experience,
            leveled_up=bool(random.randint(0, 1)),
            user_id=user_id,
            created_at=None,  # Use default
            updated_at=None,  # Use default
        )
        adventurers.append(adventurer)
    
    return adventurers


def generate_quests(count: int, adventurers: List[Adventurer]) -> List[Quest]:
    """Generate RPG-themed quests for the adventurers.
    
    Args:
        count: Number of quests to generate
        adventurers: List of adventurers to assign quests to
        
    Returns:
        List[Quest]: A list of Quest objects
    """
    quest_titles = [
        "Defeat the Dragon of Doom",
        "Rescue the Princess from the Tower",
        "Find the Lost Artifact of Power",
        "Clear the Goblin Cave",
        "Escort the Merchant to Safety",
        "Brew the Potion of Eternal Youth",
        "Solve the Ancient Riddle",
        "Hunt the Mythical Beast",
        "Retrieve the Stolen Crown Jewels",
        "Climb the Forbidden Mountain",
        "Explore the Haunted Mansion",
        "Deliver the Secret Message",
        "Gather Rare Herbs from the Forest",
        "Win the Tournament of Champions",
        "Break the Curse of the Ancient Tomb"
    ]
    
    quests = []
    for i in range(min(count, len(quest_titles))):
        # Randomly assign to an adventurer
        adventurer = random.choice(adventurers)
        experience_reward = random.randint(50, 500)
        
        quest = Quest(
            id=str(uuid.uuid4()),
            adventurer_id=adventurer.id,
            title=quest_titles[i],
            experience_reward=experience_reward,
            completed=False,  # We'll set this separately with completions
            created_at=None,  # Use default
            updated_at=None,  # Use default
        )
        quests.append(quest)
    
    return quests


def generate_quest_completions(quests: List[Quest], completion_percentage: float = 0.3) -> Tuple[List[QuestCompletion], List[Quest]]:
    """Generate quest completions for a subset of quests.
    
    Args:
        quests: List of quests to potentially mark as completed
        completion_percentage: Percentage of quests to mark as completed (0.0 to 1.0)
        
    Returns:
        Tuple[List[QuestCompletion], List[Quest]]: 
            - List of QuestCompletion objects
            - Updated list of Quest objects with completion status
    """
    num_completions = int(len(quests) * completion_percentage)
    completed_quests = random.sample(quests, num_completions)
    
    quest_completions = []
    for quest in completed_quests:
        # Mark the quest as completed
        quest.completed = True # type: ignore
        
        quest_completion = QuestCompletion(
            id=str(uuid.uuid4()),
            adventurer_id=quest.adventurer_id,
            quest_id=quest.id,
            created_at=None,  # Use default
            updated_at=None,  # Use default
        )
        quest_completions.append(quest_completion)
    
    return quest_completions, quests


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def get_seed_data() -> Dict[str, List]:
    """Get all seed data for the application.
    
    Returns:
        Dict[str, List]: Dictionary containing all seed data organized by model type
    """
    # Create admin user
    user = generate_user()
    
    # Create adventurers (5-10)
    adventurer_count = random.randint(5, 10)
    adventurers = generate_adventurers(adventurer_count, user.id) # type: ignore
    
    # Create quests (10-15)
    quest_count = random.randint(10, 15)
    quests = generate_quests(quest_count, adventurers)
    
    # Create quest completions for ~30% of quests
    quest_completions, updated_quests = generate_quest_completions(quests, 0.3)
    
    return {
        "users": [user],
        "adventurers": adventurers,
        "quests": updated_quests,
        "quest_completions": quest_completions
    } 