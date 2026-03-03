"""
Base SQLModel classes and utilities.

This module provides the foundation for all database models.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin that adds created_at and updated_at timestamp fields."""
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Last update timestamp",
    )


class BaseModel(TimestampMixin):
    """Base model with common fields."""
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
