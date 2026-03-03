"""
User management endpoints.

Provides:
- List users
- Get user by ID
- Update user
- Delete user
"""

from typing import AsyncGenerator, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_superuser
from app.database import get_db_manager
from app.models.user import User
from app.schemas import Message, PaginatedResponse, UserCreate, UserResponse, UserUpdate
from app.services import UserService


router = APIRouter(prefix="/users", tags=["Users"])


async def get_db() -> AsyncGenerator:
    """Dependency to get database session."""
    async for session in get_db_manager().session():
        yield session


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users (paginated)."""
    async for session in db:
        users = await UserService.list_users(session, skip=skip, limit=limit)
        return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    async for session in db:
        user = await UserService.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user information."""
    async for session in db:
        user = await UserService.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Only allow users to update their own profile (unless superuser)
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        
        updated_user = await UserService.update_user(session, user, user_in)
        return updated_user


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (superuser only)."""
    async for session in db:
        success = await UserService.delete_user(session, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return Message(message=f"User {user_id} deleted successfully")
