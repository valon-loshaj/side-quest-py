from typing import Tuple, Any

from flask import Blueprint, Response, jsonify, request, g, current_app
import logging

from ..models.adventurer import AdventurerNotFoundError, AdventurerValidationError
from ..services.adventurer_service import AdventurerService
from ..services.auth_service import AuthService
from functools import wraps
from ..models.db_models import Adventurer

adventurer_bp = Blueprint("adventurer", __name__)
adventurer_service = AdventurerService()
auth_service = AuthService()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adventurer_routes")


# Helper decorator for routes that require authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        try:
            # Get the token from the Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                logger.error("No Authorization header provided")
                return jsonify({"error": "Authorization header is required"}), 401

            # The format should be "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                logger.error(f"Invalid Authorization header format: {auth_header}")
                return jsonify({"error": "Authorization header must be in the format: Bearer <token>"}), 401

            token = parts[1]
            logger.info(f"Token received: {token[:10]}... (length: {len(token)})")

            # Log token parts for debugging
            token_parts = token.split(".")
            logger.info(f"Token parts count: {len(token_parts)}")

            # Validate the token and get the user
            user = auth_service.validate_token(token)
            if not user:
                logger.error("Token validation failed - no user found for this token")
                return jsonify({"error": "Invalid or expired token"}), 401

            # Store the user in g for later use in the route
            g.user = user
            logger.info(f"Authentication successful for user: {user.username}")

            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Authentication error: {str(e)}")
            return jsonify({"error": f"Authentication error: {str(e)}"}), 500

    return decorated_function


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
        user_id = data.get("user_id")

        if not name:
            return jsonify({"error": "Name is required"}), 400
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        level = data.get("level", 1)
        experience = data.get("experience", 0)

        adventurer = adventurer_service.create_adventurer(
            name=name, user_id=user_id, level=level, experience=experience
        )

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
@login_required
def get_all_adventurers() -> Tuple[Response, int]:
    """Get all adventurers for the authenticated user.

    Returns:
        Tuple[Response, int]: The list of user's adventurers and HTTP status code
    """
    try:
        # Get the authenticated user from Flask's g object
        user = g.user
        user_id = user.id
        logger.info(f"Fetching adventurers for user ID: {user_id}")

        # Retrieve only adventurers belonging to this user
        adventurers = Adventurer.query.filter_by(user_id=user_id).all()
        logger.info(f"Found {len(adventurers)} adventurers for user")

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
        logger.exception(f"Error fetching adventurers: {str(e)}")
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
