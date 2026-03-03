"""
Database connection and session management.

Supports SQLite, MySQL, and PostgreSQL with async SQLModel.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel

from app.config import DatabaseConfig, get_settings


class Base(SQLModel, DeclarativeBase):
    """Base class for all database models."""
    pass


class DatabaseManager:
    """
    Database connection manager.
    
    Handles async engine creation, session management, and lifecycle events.
    Supports SQLite, MySQL, and PostgreSQL.
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager.
        
        Args:
            config: Database configuration. If None, loads from settings.
        """
        self._config = config
        self._engine = None
        self._session_factory = None
    
    @property
    def config(self) -> DatabaseConfig:
        """Get database configuration."""
        if self._config is None:
            self._config = get_settings().database
        return self._config
    
    @property
    def async_engine(self):
        """Get or create async engine."""
        if self._engine is None:
            # SQLite doesn't support connection pool parameters
            if self.config.type == "sqlite":
                self._engine = create_async_engine(
                    self.config.url,
                    echo=self.config.echo,
                    connect_args={"check_same_thread": self.config.sqlite.check_same_thread},
                    future=True,
                )
            else:
                self._engine = create_async_engine(
                    self.config.url,
                    echo=self.config.echo,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    pool_recycle=self.config.pool_recycle,
                    pool_pre_ping=self.config.pool_pre_ping,
                    future=True,
                )
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return self._session_factory
    
    async def init_db(self) -> None:
        """Initialize database tables."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_db(self) -> None:
        """Drop all database tables."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session.
        
        Usage:
            async with db_manager.session() as session:
                # use session
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get global database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database session.
    
    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async for session in get_db_manager().session():
        yield session


# Alias for compatibility
get_db = get_db_session
