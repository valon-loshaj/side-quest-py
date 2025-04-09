from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from ..models.user import UserNotFoundError, UserServiceError, UserValidationError
from ..services.user_service import UserService

user_bp = Blueprint("user", __name__)
user_service = UserService()


# Route 1: Create User
@user_bp.route("/user", methods=["POST"])
def create_user() -> Tuple[Response, int]:
    """
    Create a new User.

    Returns:
        Tuple[Response, int]: The created user data and the HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        email = data.get("email")

        if not username:
            return jsonify({"error": "Username is required"}), 400
        if not email:
            return jsonify({"error": "Email is required"}), 400

        user = user_service.create_user(username=username, email=email)

        return jsonify({"message": "User created successfully", "user": user_service.user_to_dict(user)}), 201

    except UserValidationError as e:
        return jsonify({"error": str(e)}), 400
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


# Route 2: Get User by ID
@user_bp.route("/user/<string:user_id>", methods=["GET"])
def get_user_by_id(user_id: str) -> Tuple[Response, int]:
    """
    Get a user by their ID.

    Returns:
        Tuple[Response, int]: The user data and the HTTP status code
    """
    try:
        user = user_service.get_user(user_id)

        if not user:
            return jsonify({"error": f"User with ID: {user_id} not found"}), 404

        return jsonify({"user": user_service.user_to_dict(user)}), 200

    except UserNotFoundError as e:
        return jsonify({"error": f"User with ID: {user_id} not found", "details": str(e)}), 404
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for user with ID: {user_id}", "details": str(e)}), 400


# Route 3: Get All Users
@user_bp.route("/users", methods=["GET"])
def get_all_users() -> Tuple[Response, int]:
    """
    Get all users.

    Returns:
        Tuple[Response, int]: The list of users and the HTTP status code
    """
    try:
        users = user_service.get_all_users()
        return jsonify([user_service.user_to_dict(user) for user in users]), 200
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


# Route 4: Update User
@user_bp.route("/user/<string:user_id>", methods=["PUT"])
def update_user(user_id: str) -> Tuple[Response, int]:
    """
    Update a user's information.

    Returns:
        Tuple[Response, int]: The updated user data and the HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        email = data.get("email")

        if not username and not email:
            return jsonify({"error": "No valid fields to update"}), 400

        user = user_service.update_user(user_id, username=username, email=email)

        return jsonify({"message": "User updated successfully", "user": user_service.user_to_dict(user)}), 200

    except UserNotFoundError as e:
        return jsonify({"error": f"User with ID: {user_id} not found", "details": str(e)}), 404
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for user with ID: {user_id}", "details": str(e)}), 400


# Route 5: Delete User
@user_bp.route("/user/<string:user_id>", methods=["DELETE"])
def delete_user(user_id: str) -> Tuple[Response, int]:
    """
    Delete a user by their ID.

    Returns:
        Tuple[Response, int]: The HTTP status code
    """
    try:
        user_service.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"}), 200
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for user with ID: {user_id}", "details": str(e)}), 400


# Route 6: Add Adventurer to User
@user_bp.route("/user/<string:user_id>/adventurer", methods=["POST"])
def add_adventurer(user_id: str) -> Tuple[Response, int]:
    """
    Add an adventurer to a user.

    Returns:
        Tuple[Response, int]: The updated user data and the HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        adventurer_id = data.get("adventurer_id")

        if not adventurer_id:
            return jsonify({"error": "Adventurer ID is required"}), 400

        user = user_service.add_adventurer(user_id, adventurer_id)

        return jsonify({"message": "Adventurer added successfully", "user": user_service.user_to_dict(user)}), 200
    except UserNotFoundError as e:
        return jsonify({"error": f"User with ID: {user_id} not found", "details": str(e)}), 404
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input for user with ID: {user_id}", "details": str(e)}), 400
