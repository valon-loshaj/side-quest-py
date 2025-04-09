from functools import wraps
from typing import Any, Tuple

from flask import Blueprint, Response, g, jsonify, request

from ..models.user import (
    AuthenticationError,
    UserNotFoundError,
    UserServiceError,
    UserValidationError,
)
from ..services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


# Helper decorator for routes that require authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
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

    return decorated_function


@auth_bp.route("/register", methods=["POST"])
def register() -> Tuple[Response, int]:
    """
    Register a new user.

    Returns:
        Tuple[Response, int]: The created user data and the HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username:
            return jsonify({"error": "Username is required"}), 400
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400

        user = auth_service.register_user(username=username, email=email, password=password)

        return (
            jsonify({"message": "User registered successfully", "user": auth_service.user_service.user_to_dict(user)}),
            201,
        )

    except UserValidationError as e:
        return jsonify({"error": str(e)}), 400
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login() -> Tuple[Response, int]:
    """
    Authenticate a user and provide an authentication token.

    Returns:
        Tuple[Response, int]: The authentication token and the HTTP status code
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username:
            return jsonify({"error": "Username is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400

        user, token = auth_service.authenticate(username=username, password=password)

        return (
            jsonify(
                {
                    "message": "Authentication successful",
                    "auth_token": token,
                    "user": auth_service.user_service.user_to_dict(user),
                }
            ),
            200,
        )

    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout() -> Tuple[Response, int]:
    """
    Logout a user by invalidating their authentication token.

    Returns:
        Tuple[Response, int]: A success message and the HTTP status code
    """
    try:
        user = g.user
        auth_service.logout(user.id)
        return jsonify({"message": "Logout successful"}), 200

    except UserNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


# Get the current authenticated user based on the token in the Authorization header
@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user() -> Tuple[Response, int]:
    """
    Get the current authenticated user.

    Returns:
        Tuple[Response, int]: The user data and the HTTP status code
    """
    try:
        user = g.user
        return jsonify({"user": auth_service.user_service.user_to_dict(user)}), 200

    except UserNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except UserServiceError as e:
        return jsonify({"error": str(e)}), 500
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
