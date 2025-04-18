from typing import Tuple, Any

from flask import Blueprint, Response, jsonify, request, g

from ..models.quest import (
    QuestNotFoundError,
    QuestValidationError,
)
from ..services.quest_service import QuestService, QuestServiceError
from ..services.auth_service import AuthService
from functools import wraps

quest_bp = Blueprint("quest", __name__)
quest_service = QuestService()
auth_service = AuthService()


# Helper decorator for routes that require authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        try:
            # Get the token from the Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Authorization header is required"}), 401

            # The format should be "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"error": "Authorization header must be in the format: Bearer <token>"}), 401

            token = parts[1]

            # Validate the token and get the user
            user = auth_service.validate_token(token)
            if not user:
                return jsonify({"error": "Invalid or expired token"}), 401

            # Store the user in g for later use in the route
            g.user = user

            return f(*args, **kwargs)
        except (TypeError, ValueError) as e:
            return jsonify({"error": f"Unexpected error validating bearer token: {str(e)}"}), 500

    return decorated_function


# Route 1: Create Quest
@quest_bp.route("/quest", methods=["POST"])
@login_required
def create_quest() -> Tuple[Response, int]:
    """
    Create a new Quest.

    Returns:
        Tuple[Response, int]: The created quest data and the HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        adventurer_id = data.get("adventurer_id")
        experience_reward = 100

        if not title:
            return jsonify({"error": "Title for quest was not provided"}), 400

        quest = quest_service.create_quest(
            title=title,
            adventurer_id=adventurer_id,
            experience_reward=experience_reward,
        )

        return (
            jsonify(
                {
                    "message": f"Quest {title} created successfully",
                    "quest": quest_service.quest_to_dict(quest),
                }
            ),
            201,
        )

    except QuestValidationError as e:
        return jsonify({"error": str(e)}), 400
    except QuestServiceError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# Route 2: Update Quest
@quest_bp.route("/quest/<string:quest_id>", methods=["PATCH"])
@login_required
def update_quest(quest_id: str) -> Tuple[Response, int]:
    """
    Update an existing quest with partial data.

    Args:
        quest_id: The ID of the quest to update

    Returns:
        Tuple[Response, int]: The quest data that was updated and HTTP status code
    """
    try:
        existing_quest = quest_service.get_quest(quest_id)

        if not existing_quest:
            return jsonify({"error": f"Quest with ID: {quest_id} not found"}), 404

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Initialize update parameters
        title = None
        adventurer_id = None
        experience_reward = None
        completed = None

        # Extract fields that are present in the request
        if "title" in data:
            title = data["title"]

        if "adventurer_id" in data:
            adventurer_id = data["adventurer_id"]

        if "experience_reward" in data:
            experience_reward = int(data["experience_reward"])

        if "completed" in data:
            completed = bool(data["completed"])

        # Call the service with properly typed parameters
        updated_quest = quest_service.update_quest(
            quest_id=quest_id,
            title=title,
            adventurer_id=adventurer_id,
            experience_reward=experience_reward,
            completed=completed,
        )
        quest_dict = quest_service.quest_to_dict(updated_quest)

        return (
            jsonify({"message": f"Quest with ID: {quest_id} updated", "quest": quest_dict}),
            200,
        )
    except QuestNotFoundError as e:
        return jsonify({"error": f"Quest with ID: {quest_id} not found", "details": str(e)}), 404
    except QuestServiceError as e:
        return jsonify({"error": f"Error updating quest with ID: {quest_id}", "details": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for quest with ID: {quest_id}", "details": str(e)}), 400


# Route 3: Get Quests
@quest_bp.route("/quests/<string:adventurer_id>", methods=["GET"])
@login_required
def get_quests(adventurer_id: str) -> Tuple[Response, int]:
    """
    Get all quests

    Returns:
        Tuple[Response, int]: The list of quests and HTTP status code
    """
    try:
        quests = quest_service.get_all_quests(adventurer_id)
        return jsonify([quest_service.quest_to_dict(quest) for quest in quests]), 200
    except QuestServiceError as e:
        return jsonify({"error": str(e)}), 500


# Route 4: Get Quest by ID
@quest_bp.route("/quest/<string:quest_id>", methods=["GET"])
@login_required
def get_quest_by_id(quest_id: str) -> Tuple[Response, int]:
    """
    Get a quest by its ID

    Args:
        quest_id: The ID of the quest

    Returns:
        Tuple[Response, int]: The quest data and HTTP status code
    """
    try:
        quest = quest_service.get_quest(quest_id)
        if not quest:
            return jsonify({"error": f"Quest with ID: {quest_id} not found"}), 404
        return jsonify({"quest": quest_service.quest_to_dict(quest)}), 200
    except QuestNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except QuestServiceError as e:
        return jsonify({"error": str(e)}), 500


# Route 5: Delete Quest by ID
@quest_bp.route("/quest/<string:quest_id>", methods=["DELETE"])
@login_required
def delete_quest(quest_id: str) -> Tuple[Response, int]:
    """
    Delete a quest by its ID

    Args:
        quest_id: The ID of the quest to delete

    Returns:
        Tuple[Response, int]: Response message and HTTP status code
    """
    try:
        quest = quest_service.get_quest(quest_id)
        if not quest:
            return jsonify({"error": f"Quest with ID: {quest_id} not found"}), 404

        quest_service.delete_quest(quest_id)
        return jsonify({"message": f"Quest with ID: {quest_id} deleted successfully"}), 200
    except QuestNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except QuestServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for quest with ID: {quest_id}", "details": str(e)}), 400
