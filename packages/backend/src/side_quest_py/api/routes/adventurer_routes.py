"""
This module contains the routes for the adventurer endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from src.side_quest_py.api.schemas.adventurer import AdventurerCreate, AdventurerUpdate, AdventurerResponse
from src.side_quest_py.services.adventurer_service import AdventurerService
from src.side_quest_py.services.auth_service import AuthService
from src.side_quest_py.api.deps.auth_helpers import extract_token_from_header, verify_auth_token
from pydantic import ValidationError
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["adventurer"])


@router.post("/adventurer", response_model=AdventurerResponse, status_code=status.HTTP_201_CREATED)
async def create_adventurer(
    request: Request,
    auth_service: AuthService = Depends(),
    adventurer_service: AdventurerService = Depends(),
):
    """
    Create a new adventurer.

    This endpoint allows users to create a new adventurer.

    Args:
        adventurer: The adventurer to create
        user: The authenticated user (injected by the validate_token dependency)

    Returns:
        The created adventurer
    """
    try:
        request_body = await request.json()
        if not request_body:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body is required")

        try:
            adventurer_data = AdventurerCreate(**request_body)
        except ValidationError as e:
            simplified_errors = {}
            for error in e.errors():
                field = error["loc"][-1] if len(error["loc"]) > 0 else "general"
                simplified_errors[field] = error["msg"]

            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"errors": simplified_errors})

        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)

        user_id_str = str(user.id)
        created_adventurer = await adventurer_service.create_adventurer(
            name=adventurer_data.name, user_id=user_id_str, adventurer_type=adventurer_data.adventurer_type
        )
        return adventurer_service.adventurer_to_dict(created_adventurer)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put("/adventurer/{adventurer_id}", response_model=AdventurerResponse)
async def update_adventurer(
    adventurer_id: str,
    adventurer_update: AdventurerUpdate,
    request: Request,
    auth_service: AuthService = Depends(),
    adventurer_service: AdventurerService = Depends(),
):
    """
    Update an adventurer's properties.

    Args:
        adventurer_id: The ID of the adventurer to update
        adventurer_update: The properties to update
        request: The request object
        auth_service: The auth service
        adventurer_service: The adventurer service

    Returns:
        The updated adventurer

    Raises:
        HTTPException: If authentication fails or adventurer not found
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        update_data = {k: v for k, v in adventurer_update.model_dump().items() if v is not None}

        updated_adventurer = await adventurer_service.update_adventurer(adventurer_id, **update_data)

        if not updated_adventurer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Adventurer with ID {adventurer_id} not found"
            )

        return adventurer_service.adventurer_to_dict(updated_adventurer)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete("/adventurer/{adventurer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adventurer(
    adventurer_id: str,
    request: Request,
    auth_service: AuthService = Depends(),
    adventurer_service: AdventurerService = Depends(),
):
    """
    Delete an adventurer by ID.

    Args:
        adventurer_id: The ID of the adventurer to delete
        request: The request object
        auth_service: The auth service
        adventurer_service: The adventurer service

    Returns:
        The deleted adventurer
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        success = await adventurer_service.delete_adventurer(adventurer_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adventurer not found")

        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/adventurers", response_model=List[AdventurerResponse])
async def get_all_adventurers(
    request: Request,
    auth_service: AuthService = Depends(),
    adventurer_service: AdventurerService = Depends(),
):
    """
    Get all adventurers.

    Args:
        request: The request object
        auth_service: The auth service
        adventurer_service: The adventurer service

    Returns:
        A list of all adventurers
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        current_user_id: str = user.id
        adventurers = await adventurer_service.get_all_adventurers(current_user_id)
        return [adventurer_service.adventurer_to_dict(adventurer) for adventurer in adventurers]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/adventurer/{adventurer_id}", response_model=AdventurerResponse)
async def get_adventurer_by_id(
    adventurer_id: str,
    request: Request,
    auth_service: AuthService = Depends(),
    adventurer_service: AdventurerService = Depends(),
):
    """
    Get an adventurer by ID.

    Args:
        adventurer_id: The ID of the adventurer to get
        request: The request object
        auth_service: The auth service
        adventurer_service: The adventurer service

    Returns:
        The adventurer
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        adventurer = await adventurer_service.get_adventurer_by_id(adventurer_id)
        if not adventurer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adventurer not found")

        return adventurer_service.adventurer_to_dict(adventurer)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
