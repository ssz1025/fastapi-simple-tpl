"""
SQLModel database models.

All database models should inherit from `app.database.Base`.
"""

from app.database import Base

# Import your models here and add them to __all__
# Example:
# from .user import User
# __all__ = ["User", "Base"]

__all__ = ["Base"]
