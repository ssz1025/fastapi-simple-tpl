"""
Pydantic schemas for request/response validation.

This module contains all Pydantic models used for:
- Request body validation
- Response serialization
- API documentation
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    username: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive fields)."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Schema for user stored in database (includes password hash)."""
    hashed_password: str

    class Config:
        from_attributes = True


# =============================================================================
# Auth Schemas
# =============================================================================

class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# =============================================================================
# Common Schemas
# =============================================================================

class Message(BaseModel):
    """Generic message response."""
    message: str


class ErrorDetail(BaseModel):
    """Detailed error response."""
    error: str
    detail: Optional[str] = None
    field: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Health Check Schemas
# =============================================================================

class HealthStatus(BaseModel):
    """Health check status."""
    status: str  # healthy, degraded, unhealthy
    database: str = "unknown"
    redis: str = "unknown"


class ComponentHealth(BaseModel):
    """Individual component health."""
    status: str
    details: Optional[dict] = None
