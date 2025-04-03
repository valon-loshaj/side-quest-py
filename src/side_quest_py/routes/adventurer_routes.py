from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
from src.side_quest_py.services.adventurer_service import AdventurerService
from src.side_quest_py.models.adventurer import AdventurerValidationError

adventurer_bp = Blueprint('adventurer', __name__)
adventurer_service = AdventurerService()

@adventurer_bp.route('/adventurer', methods=['POST'])
def create_adventurer() -> Tuple[Dict[str, Any], int]:
    """Create a new adventurer.
    
    Returns:
        Tuple[Dict[str, Any], int]: The created adventurer data and HTTP status code
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
            
        level = data.get('level', 1)
        experience = data.get('experience', 0)
        
        adventurer = adventurer_service.create_adventurer(
            name=name,
            level=level,
            experience=experience
        )
        
        return jsonify({
            "message": f"Adventurer {name} created successfully",
            "adventurer": adventurer_service.adventurer_to_dict(adventurer)
        }), 201
        
    except AdventurerValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@adventurer_bp.route('/adventurer/<name>', methods=['GET'])
def get_adventurer(name: str) -> Tuple[Dict[str, Any], int]:
    """Get an adventurer by name.
    
    Args:
        name: The name of the adventurer
        
    Returns:
        Tuple[Dict[str, Any], int]: The adventurer data and HTTP status code
    """
    try:
        adventurer = adventurer_service.get_adventurer(name)
        
        if not adventurer:
            return jsonify({"error": f"Adventurer {name} not found"}), 404
            
        return jsonify({
            "adventurer": adventurer_service.adventurer_to_dict(adventurer)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@adventurer_bp.route('/adventurers', methods=['GET'])
def get_all_adventurers() -> Tuple[Dict[str, Any], int]:
    """Get all adventurers.
    
    Returns:
        Tuple[Dict[str, Any], int]: The list of adventurers and HTTP status code
    """
    try:
        adventurers = adventurer_service.get_all_adventurers()
        
        return jsonify({
            "adventurers": [
                adventurer_service.adventurer_to_dict(adventurer) 
                for adventurer in adventurers
            ],
            "count": len(adventurers)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500 