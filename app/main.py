"""
FastAPI Application Entry Point.

Provides:
- Application lifecycle management (startup/shutdown)
- Database initialization
- Redis connection
- CORS configuration
- API routes
- Structured logging
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import get_settings
from app.database import get_db_manager
from app.redis_client import get_redis_manager
from app.api.v1.endpoints import health
from app.routers.v1 import auth, users


# Configure logging
settings = get_settings()

logging.basicConfig(
    level=settings.logging.level,
    format=settings.logging.format,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Initialize database tables
    - Connect to Redis
    - Cleanup on shutdown
    """
    logger.info(f"Starting {settings.app.name} in {settings.environment} mode")
    
    # Startup
    db_manager = get_db_manager()
    try:
        await db_manager.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    redis_manager = get_redis_manager()
    await redis_manager.connect()
    if redis_manager.is_available:
        logger.info("Redis connected")
    else:
        logger.warning("Redis not available, continuing without caching")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await redis_manager.disconnect()
    await db_manager.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan,
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests with timing information."""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )
        
        return response
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    # Health check
    app.include_router(
        health.router,
        prefix=f"{settings.app.api_prefix}/health",
        tags=["Health"],
    )
    
    # Auth routes
    app.include_router(
        auth.router,
        prefix=settings.app.api_prefix,
    )
    
    # User management routes
    app.include_router(
        users.router,
        prefix=settings.app.api_prefix,
    )
    
    return app


# Create application instance
app = create_app()


# Application info endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "environment": settings.environment,
    }


# Application info endpoint with more detail
@app.get("/info")
async def info():
    """Application information endpoint."""
    db_config = get_settings().database
    redis_config = get_settings().redis
    
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "environment": settings.environment,
        "debug": settings.app.debug,
        "database": {
            "type": db_config.type,
            "url": "sqlite" if db_config.type == "sqlite" else str(db_config.url).split("@")[-1] if "@" in str(db_config.url) else str(db_config.url),
        },
        "redis": {
            "enabled": redis_config.enabled,
            "mode": redis_config.mode,
            "available": get_redis_manager().is_available,
        },
    }
