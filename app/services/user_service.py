"""
User service layer.

Contains business logic for user operations.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas import UserCreate, UserUpdate


class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_in.password)
        
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def update_user(
        db: AsyncSession, 
        db_user: User, 
        user_in: UserUpdate
    ) -> User:
        """Update user information."""
        update_data = user_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user by email and password."""
        user = await UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def list_users(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[User]:
        """List users with pagination."""
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Delete a user by ID."""
        user = await UserService.get_user_by_id(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False
