"""
Health check endpoints.

Provides:
- Basic health check
- Database health check
- Redis health check
- Full system health check
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text

from app.config import get_settings
from app.database import get_db_manager
from app.redis_client import get_redis_manager
from pydantic import BaseModel

from app.config import get_settings
from app.database import get_db_manager
from app.redis_client import get_redis_manager
from pydantic import BaseModel

from app.database import get_db_manager
from app.redis_client import get_redis_manager


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    database: str = "unknown"
    redis: str = "unknown"


class DatabaseHealthResponse(BaseModel):
    """Database health check response."""
    status: str
    type: str
    available: bool


class RedisHealthResponse(BaseModel):
    """Redis health check response."""
    status: str
    mode: str
    available: bool


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns overall health status of all components.
    """
    # Check database
    db_status = "healthy"
    try:
        db_manager = get_db_manager()
        async with db_manager.session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
    
    # Check Redis
    redis_status = "healthy"
    redis_manager = get_redis_manager()
    if not redis_manager.is_enabled:
        redis_status = "disabled"
    elif not redis_manager.is_available:
        redis_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    if redis_status == "unhealthy":
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
    )


@router.get("/database", response_model=DatabaseHealthResponse)
async def database_health():
    """
    Database health check endpoint.
    
    Returns database connection status.
    """
    settings = get_settings()
    db_manager = get_db_manager()
    
    try:
        async with db_manager.session() as session:
            await session.execute(text("SELECT 1"))
        return DatabaseHealthResponse(
            status="healthy",
            type=settings.database.type,
            available=True,
        )
    except Exception as e:
        return DatabaseHealthResponse(
            status="unhealthy",
            type=settings.database.type,
            available=False,
        )


@router.get("/redis", response_model=RedisHealthResponse)
async def redis_health():
    """
    Redis health check endpoint.
    
    Returns Redis connection status.
    """
    settings = get_settings()
    redis_manager = get_redis_manager()
    
    if not redis_manager.is_enabled:
        return RedisHealthResponse(
            status="disabled",
            mode=settings.redis.mode,
            available=False,
        )
    
    is_available = await redis_manager.ping()
    
    return RedisHealthResponse(
        status="healthy" if is_available else "unhealthy",
        mode=settings.redis.mode,
        available=is_available,
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe endpoint.
    
    Used by Kubernetes/container orchestrators to check if app is ready.
    """
    db_manager = get_db_manager()
    redis_manager = get_redis_manager()
    
    # Check database
    try:
        async with db_manager.session() as session:
            await session.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False
    
    # Check Redis if enabled
    redis_ready = True
    if redis_manager.is_enabled:
        redis_ready = redis_manager.is_available
    
    if db_ready and redis_ready:
        return {"status": "ready"}
    else:
        return {"status": "not ready"}


@router.get("/live")
async def liveness_check():
    """
    Liveness probe endpoint.
    
    Used by Kubernetes/container orchestrators to check if app is alive.
    """
    return {"status": "alive"}
