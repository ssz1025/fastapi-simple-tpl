"""
API Response wrappers.

Provides standardized response formats for FastAPI endpoints.
"""

from typing import Any, Generic, List, Optional, TypeVar

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    code: int = status.HTTP_200_OK

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: int = status.HTTP_400_BAD_REQUEST

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Create a success JSON response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        JSONResponse
    """
    content = {
        "success": True,
        "message": message,
        "data": data,
    }
    return JSONResponse(content=content, status_code=status_code)


def error_response(
    error: str,
    detail: Optional[str] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """
    Create an error JSON response.
    
    Args:
        error: Error type/title
        detail: Detailed error message
        status_code: HTTP status code
        
    Returns:
        JSONResponse
    """
    content = {
        "success": False,
        "error": error,
        "detail": detail,
    }
    return JSONResponse(content=content, status_code=status_code)


def paginate(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse:
    """
    Create a paginated response.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        PaginatedResponse
    """
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def not_found(resource: str = "Resource") -> JSONResponse:
    """Create a 404 not found response."""
    return error_response(
        error=f"{resource} not found",
        detail=f"The requested {resource.lower()} was not found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


def unauthorized(message: str = "Unauthorized") -> JSONResponse:
    """Create a 401 unauthorized response."""
    return error_response(
        error="Unauthorized",
        detail=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


def forbidden(message: str = "Forbidden") -> JSONResponse:
    """Create a 403 forbidden response."""
    return error_response(
        error="Forbidden",
        detail=message,
        status_code=status.HTTP_403_FORBIDDEN,
    )


def bad_request(message: str = "Bad Request") -> JSONResponse:
    """Create a 400 bad request response."""
    return error_response(
        error="Bad Request",
        detail=message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def internal_error(message: str = "Internal Server Error") -> JSONResponse:
    """Create a 500 internal error response."""
    return error_response(
        error="Internal Server Error",
        detail=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
