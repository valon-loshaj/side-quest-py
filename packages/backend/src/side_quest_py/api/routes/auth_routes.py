"""
This module contains the routes for the authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.side_quest_py.api.schemas.auth import Token, UserCreate, UserResponse
from src.side_quest_py.services.auth_service import AuthService
from src.side_quest_py.api.deps.auth_helpers import extract_token_from_header, verify_auth_token

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, auth_service: AuthService = Depends()):
    """
    Register a new user.

    This endpoint allows users to create a new account.

    Args:
        user_data: The user data for registration

    Returns:
        The newly created user

    Raises:
        HTTPException: If username or email already exists or if registration fails
    """
    try:
        new_user = auth_service.register_user(
            username=user_data.username, email=user_data.email, password=user_data.password
        )
        return new_user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(exc)}"
        ) from exc


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends()):
    """
    Authenticate a user and issue an access token.

    This endpoint validates user credentials and issues a JWT token for authentication.

    Args:
        form_data: The username and password for authentication

    Returns:
        A token object containing the access token

    Raises:
        HTTPException: If authentication fails
    """
    try:
        access_token = auth_service.authenticate_user(username=form_data.username, password=form_data.password)

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login failed: {str(exc)}"
        ) from exc


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, auth_service: AuthService = Depends()):
    """
    Logout a user by invalidating their authentication token.

    Args:
        request: The FastAPI request object
        auth_service: The auth service

    Returns:
        A success message

    Raises:
        HTTPException: If logout fails
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        current_user_id = str(user.id)
        auth_service.logout_user(current_user_id)
        return {"detail": "Successfully logged out"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Logout failed: {str(exc)}"
        ) from exc


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user(request: Request, auth_service: AuthService = Depends()):
    """
    Get the current user's information.
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        # Get the db user model instead of the token user model
        return auth_service.user_to_dict(user)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get current user: {str(exc)}"
        ) from exc
