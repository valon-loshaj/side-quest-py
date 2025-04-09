from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from ..models.adventurer import AdventurerNotFoundError, AdventurerValidationError
from ..services.adventurer_service import AdventurerService

adventurer_bp = Blueprint("adventurer", __name__)
adventurer_service = AdventurerService()


@adventurer_bp.route("/adventurer", methods=["POST"])
def create_adventurer() -> Tuple[Response, int]:
    """Create a new adventurer.

    Returns:
        Tuple[Response, int]: The created adventurer data and HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        name = data.get("name")

        if not name:
            return jsonify({"error": "Name is required"}), 400

        level = data.get("level", 1)
        experience = data.get("experience", 0)

        adventurer = adventurer_service.create_adventurer(name=name, level=level, experience=experience)

        return (
            jsonify(
                {
                    "message": f"Adventurer {name} created successfully",
                    "adventurer": adventurer_service.adventurer_to_dict(adventurer),
                }
            ),
            201,
        )

    except AdventurerValidationError as e:
        return jsonify({"error": str(e)}), 400
    except AdventurerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@adventurer_bp.route("/adventurer/<name>", methods=["GET"])
def get_adventurer(name: str) -> Tuple[Response, int]:
    """Get an adventurer by name.

    Args:
        name: The name of the adventurer

    Returns:
        Tuple[Response, int]: The adventurer data and HTTP status code
    """
    try:
        adventurer = adventurer_service.get_adventurer(name)

        if not adventurer:
            return jsonify({"error": f"Adventurer {name} not found"}), 404

        return (
            jsonify({"adventurer": adventurer_service.adventurer_to_dict(adventurer)}),
            200,
        )

    except (TypeError, ValueError) as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@adventurer_bp.route("/adventurers", methods=["GET"])
def get_all_adventurers() -> Tuple[Response, int]:
    """Get all adventurers.

    Returns:
        Tuple[Response, int]: The list of adventurers and HTTP status code
    """
    try:
        adventurers = adventurer_service.get_all_adventurers()

        return (
            jsonify(
                {
                    "adventurers": [adventurer_service.adventurer_to_dict(adventurer) for adventurer in adventurers],
                    "count": len(adventurers),
                }
            ),
            200,
        )

    except (TypeError, ValueError) as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@adventurer_bp.route("/adventurer/<name>/quest/<quest_id>", methods=["POST"])
def complete_quest(name: str, quest_id: str) -> Tuple[Response, int]:
    """Record quest completion for an adventurer.

    Args:
        name: The name of the adventurer
        quest_id: The ID of the quest

    Returns:
        Tuple[Response, int]: The result and HTTP status code
    """
    try:
        data = request.get_json() or {}
        experience_gain = data.get("experience_gain", 0)

        result = adventurer_service.complete_quest(name, quest_id, experience_gain)

        if result is None:
            return jsonify({"error": f"Adventurer {name} not found"}), 404

        adventurer = adventurer_service.get_adventurer(name)
        assert adventurer is not None

        return (
            jsonify(
                {
                    "message": f"Quest {quest_id} processed for adventurer {name}",
                    "was_new_completion": result["was_new_completion"],
                    "leveled_up": result["leveled_up"],
                    "adventurer": adventurer_service.adventurer_to_dict(adventurer),
                }
            ),
            200,
        )

    except AdventurerValidationError as e:
        return jsonify({"error": str(e)}), 400
    except TypeError as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
