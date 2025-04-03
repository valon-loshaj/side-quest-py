from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
from src.side_quest_py.services.quest_service import QuestService
from src.side_quest_py.models.quest import QuestValidationError, QuestCompletionError

quest_bp = Blueprint('quest', __name__)
quest_service = QuestService()

# Route 1: Create Quest
@quest_bp.route('/quest', methods=['POST'])
def create_quest() -> Tuple[Dict[str, Any], int]:
    """
    Create a new Quest.

    Returns:
        Tuple[Dict[str, Any], int]: The created quest data and the HTTP status code
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get('title')
        
        if not title:
            return jsonify({"error": "Title for quest was not provided"}), 400
        
        quest = quest_service.create_quest(
            title=title
        )
        
        return jsonify({
            "message": f"Quest {title} created successfully",
            "quest": quest_service.quest_to_dict(quest)
        }), 201
        
    except QuestValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
        

# Route 2: Complete Quest
@quest_bp.route('/quest/<string:quest_id>', methods=['PATCH'])
def complete_quest(quest_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Update an existing quest as completed

    Args:
        quest_id: The ID of the quest to complete

    Returns:
        Tuple[Dict[str, Any], int]: The quest data that was updated and HTTP status code
    """
    try: 
        existing_quest = quest_service.get_quest(quest_id)
        
        if not existing_quest:
            return jsonify({"error": f"Quest with ID: {quest_id} not found"}), 404
        if existing_quest.completed:
            return jsonify({"error": f"Quest with ID: {quest_id} already complete"}), 409
        
        updated_quest = quest_service.complete_quest(quest_id)
        quest_dict = quest_service.quest_to_dict(updated_quest)
        return jsonify({
            "message": f"Quest with ID: {quest_id} completed",
            "quest": quest_dict
        }), 200
    except QuestCompletionError as e:
        return jsonify({"error": f"Unable to complete quest with ID: {quest_id}"}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error occurred when completing quest with ID: {quest_id}"}), 500


# Route 3: Get Quests
@quest_bp.route('/quests', methods=['GET'])
def get_quests() -> Tuple[Dict[str, Any], int]:
    """
    Get all quests
    """
    try:
        quests = quest_service.get_all_quests()
        return jsonify([quest_service.quest_to_dict(quest) for quest in quests]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Route 4: Get Quest by ID
@quest_bp.route('/quest/<string:quest_id>', methods=['GET'])
def get_quest_by_id(quest_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get a quest by its ID
    """
    try:
        quest = quest_service.get_quest(quest_id)
        if not quest:
            return jsonify({"error": f"Quest with ID: {quest_id} not found"}), 404
        return jsonify({"quest": quest_service.quest_to_dict(quest)}), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500