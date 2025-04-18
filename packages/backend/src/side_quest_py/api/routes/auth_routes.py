"""
This module contains the routes for the authentication endpoints.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ulid import ULID

from src.side_quest_py.database import get_db
from src.side_quest_py.api.schemas.auth import Token, UserCreate, UserResponse
from src.side_quest_py.api.auth.jwt import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.side_quest_py.models.db_models import User

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    try:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

        existing_user_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_user_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            id=str(ULID()),
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return new_user


# @router.post("/login", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     """
#     Login a user.
#     """
#     # Find user by username
#     user = db.query(User).filter(User.username == form_data.username).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # Verify password
#     if not verify_password(form_data.password, str(user.password_hash)):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # Create access token
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(jwt_payload={"sub": user.username}, expires_delta=access_token_expires)

#     # Update user's token in DB
#     user.auth_token = access_token
#     from datetime import datetime, timedelta

#     user.token_expiry = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     db.commit()

#     return {"access_token": access_token, "token_type": "bearer"}
