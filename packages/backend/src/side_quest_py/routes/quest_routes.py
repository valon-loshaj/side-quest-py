from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from ..models.quest import (
    QuestCompletionError,
    QuestNotFoundError,
    QuestValidationError,
)
from ..services.quest_service import QuestService, QuestServiceError

quest_bp = Blueprint("quest", __name__)
quest_service = QuestService()


# Route 1: Create Quest
@quest_bp.route("/quest", methods=["POST"])
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

        if not title:
            return jsonify({"error": "Title for quest was not provided"}), 400

        quest = quest_service.create_quest(title=title)

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


# Route 2: Complete Quest
@quest_bp.route("/quest/<string:quest_id>", methods=["PATCH"])
def complete_quest(quest_id: str) -> Tuple[Response, int]:
    """
    Update an existing quest as completed

    Args:
        quest_id: The ID of the quest to complete

    Returns:
        Tuple[Response, int]: The quest data that was updated and HTTP status code
    """
    try:
        existing_quest = quest_service.get_quest(quest_id)

        if not existing_quest:
            return jsonify({"error": f"Quest with ID: {quest_id} not found"}), 404
        if existing_quest.completed:
            return (
                jsonify({"error": f"Quest with ID: {quest_id} already complete"}),
                409,
            )

        updated_quest = quest_service.complete_quest(quest_id)
        quest_dict = quest_service.quest_to_dict(updated_quest)
        return (
            jsonify({"message": f"Quest with ID: {quest_id} completed", "quest": quest_dict}),
            200,
        )
    except QuestNotFoundError as e:
        return jsonify({"error": f"Quest with ID: {quest_id} not found", "details": str(e)}), 404
    except QuestCompletionError as e:
        return jsonify({"error": f"Unable to complete quest with ID: {quest_id}", "details": str(e)}), 400
    except QuestServiceError as e:
        return jsonify({"error": f"Error completing quest with ID: {quest_id}", "details": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for quest with ID: {quest_id}", "details": str(e)}), 400


# Route 3: Get Quests
@quest_bp.route("/quests", methods=["GET"])
def get_quests() -> Tuple[Response, int]:
    """
    Get all quests

    Returns:
        Tuple[Response, int]: The list of quests and HTTP status code
    """
    try:
        quests = quest_service.get_all_quests()
        return jsonify([quest_service.quest_to_dict(quest) for quest in quests]), 200
    except QuestServiceError as e:
        return jsonify({"error": str(e)}), 500


# Route 4: Get Quest by ID
@quest_bp.route("/quest/<string:quest_id>", methods=["GET"])
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
