"""
This module contains the routes for the quests endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.side_quest_py.api.schemas.quest import QuestResponse, QuestUpdate, QuestCreate
from src.side_quest_py.services.quest_service import QuestService
from src.side_quest_py.services.auth_service import AuthService
from src.side_quest_py.api.deps.auth_helpers import extract_token_from_header, verify_auth_token

router = APIRouter(prefix="/api/v1", tags=["quests"])


@router.post("/quest", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(
    request: Request,
    auth_service: AuthService = Depends(),
    quest_service: QuestService = Depends(),
):
    """
    Create a new quest.

    Args:
        request: The request object
        auth_service: The auth service
        quest_service: The quest service

    Returns:
        The created quest
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        request_body = await request.json()
        if not request_body:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body is required")

        try:
            quest_data = QuestCreate(**request_body)
        except ValidationError as e:
            simplified_errors = {}
            for error in e.errors():
                field = error["loc"][-1] if len(error["loc"]) > 0 else "general"
                simplified_errors[field] = error["msg"]

            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"errors": simplified_errors})

        created_quest = await quest_service.create_quest(
            title=quest_data.title,
            experience_reward=quest_data.experience_reward or 100,
            adventurer_id=quest_data.adventurer_id,
        )
        return quest_service.quest_to_dict(created_quest)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put("/quest/{quest_id}", response_model=QuestResponse)
async def update_quest(
    quest_id: str,
    request: Request,
    auth_service: AuthService = Depends(),
    quest_service: QuestService = Depends(),
):
    """
    Update a quest.

    Args:
        quest_id: The ID of the quest to update
        request: The request object
        auth_service: The auth service
        quest_service: The quest service

    Returns:
        The updated quest
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        request_body = await request.json()
        if not request_body:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body is required")

        try:
            quest_data = QuestUpdate(**request_body)
        except ValidationError as e:
            simplified_errors = {}
            for error in e.errors():
                field = error["loc"][-1] if len(error["loc"]) > 0 else "general"
                simplified_errors[field] = error["msg"]

            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"errors": simplified_errors})

        updated_quest = await quest_service.update_quest(
            quest_id=quest_id,
            title=quest_data.title,
            experience_reward=quest_data.experience_reward,
            adventurer_id=quest_data.adventurer_id,
            completed=quest_data.completed,
        )
        return quest_service.quest_to_dict(updated_quest)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete("/quest/{quest_id}", status_code=status.HTTP_200_OK)
async def delete_quest(
    quest_id: str,
    request: Request,
    auth_service: AuthService = Depends(),
    quest_service: QuestService = Depends(),
):
    """
    Delete a quest.

    Args:
        quest_id: The ID of the quest to delete
        request: The request object
        auth_service: The auth service
        quest_service: The quest service
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        success = await quest_service.delete_quest(quest_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quest not found")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Quest deleted successfully"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/quests/{adventurer_id}", status_code=status.HTTP_200_OK, response_model=List[QuestResponse])
async def get_all_quests(
    adventurer_id: str,
    request: Request,
    auth_service: AuthService = Depends(),
    quest_service: QuestService = Depends(),
):
    """
    Get all quests.

    Args:
        request: The request object
        auth_service: The auth service
        quest_service: The quest service

    Returns:
        A list of all quests
    """
    try:
        auth_token = extract_token_from_header(request)
        user = verify_auth_token(auth_token, auth_service)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        if not adventurer_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adventurer ID is required")

        quests = await quest_service.get_all_quests(adventurer_id)
        return [quest_service.quest_to_dict(quest) for quest in quests]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
