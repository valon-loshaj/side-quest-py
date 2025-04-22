"""
Authentication helper functions for validating requests and tokens.
"""

from fastapi import Request, HTTPException, status

from src.side_quest_py.services.auth_service import AuthService
from src.side_quest_py.models.user import User


def extract_token_from_header(request: Request) -> str:
    """
    Extract the Bearer token from the Authorization header.

    Args:
        request: The FastAPI request object

    Returns:
        The extracted token

    Raises:
        HTTPException: If Authorization header is missing or malformed
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Please provide a Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use 'Bearer your_token_here'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_header.replace("Bearer ", "")


def verify_auth_token(token: str, auth_service: AuthService) -> User:
    """
    Verify the authentication token.

    Args:
        token: The token to verify
        auth_service: The authentication service

    Returns:
        The authenticated user

    Raises:
        HTTPException: If token is invalid or expired
    """
    user = auth_service.verify_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
