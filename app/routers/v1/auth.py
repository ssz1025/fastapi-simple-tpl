"""
Authentication endpoints.

Provides:
- User registration
- User login (JWT token)
- Token refresh
- Password change
"""

from datetime import timedelta
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.core.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from app.database import get_db_manager
from app.models.user import User
from app.schemas import LoginRequest, Message, PasswordChange, Token, UserCreate, UserResponse
from app.services import UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])

settings = get_settings()


async def get_db() -> AsyncGenerator:
    """Dependency to get database session."""
    async for session in get_db_manager().session():
        yield session


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncGenerator = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_in: User registration data
        db: Database session
        
    Returns:
        Created user
    """
    async for session in db:
        # Check if email already exists
        existing_user = await UserService.get_user_by_email(session, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username exists (if provided)
        if user_in.username:
            existing_username = await UserService.get_user_by_username(session, user_in.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        user = await UserService.create_user(session, user_in)
        return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncGenerator = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns JWT access token.
    """
    async for session in db:
        user = await UserService.authenticate_user(session, form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.auth.access_token_expire_minutes * 60
        )


@router.post("/change-password", response_model=Message)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncGenerator = Depends(get_db)
):
    """Change user password."""
    async for session in db:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        from app.core.security import get_password_hash
        current_user.hashed_password = get_password_hash(password_data.new_password)
        await session.commit()
        
        return Message(message="Password updated successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
