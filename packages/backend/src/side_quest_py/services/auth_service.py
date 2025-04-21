"""
This module contains the authentication service for the Side Quest application.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ulid import ULID

from src.side_quest_py.database import get_db
from src.side_quest_py.models.db_models import User
from src.side_quest_py.api.config import settings
from src.side_quest_py.api.schemas.auth import TokenData

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication-related operations."""

    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the auth service with a database session."""
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user with a hashed password.

        Args:
            username: The username for the new user
            email: The email for the new user
            password: The plain text password for the new user

        Returns:
            User: The newly created user object

        Raises:
            HTTPException: If registration fails
        """
        if self.get_user_by_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

        if self.get_user_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        try:
            hashed_password = self.get_password_hash(password)
            new_user = User(
                id=str(ULID()),
                username=username,
                email=email,
                password_hash=hashed_password,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user

        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register user: {str(exc)}"
            ) from exc

    def authenticate_user(self, username: str, password: str) -> str:
        """
        Authenticate a user with their username and password.

        Args:
            username: The username of the user
            password: The plain text password of the user

        Returns:
            str: The access token for the authenticated user

        Raises:
            HTTPException: If authentication fails
        """
        user = self.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not self.verify_password(password, str(user.password_hash)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = self.create_access_token(data={"sub": user.username})

        # Update user's token in DB
        user.auth_token = access_token  # type: ignore
        user.token_expiry = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # type: ignore
        self.db.commit()

        return access_token

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create an access token with expiration."""
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[User]:
        """
        Verify a JWT token and return the user.

        Args:
            token: The JWT token to verify

        Returns:
            Optional[User]: The user if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                return None

            token_data = TokenData(username=username)
        except JWTError:
            return None

        user = self.get_user_by_username(username=token_data.username or "")

        if user and hasattr(user, "token_expiry") and user.token_expiry and user.token_expiry < datetime.now():  # type: ignore
            return None

        return user

    def logout_user(self, user_id: str) -> bool:
        """
        Invalidate a user's authentication token.

        Args:
            user_id: The ID of the user to log out

        Returns:
            bool: True if successful

        Raises:
            HTTPException: If logout fails
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.auth_token = None  # type: ignore
                user.token_expiry = None  # type: ignore
                self.db.commit()
                return True
            return False
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Logout failed: {str(exc)}"
            ) from exc
