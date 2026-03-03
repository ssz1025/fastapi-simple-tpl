"""
Redis client management.

Supports single Redis node and Redis Cluster modes.
Provides optional Redis (graceful degradation when Redis is unavailable).
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional, Union

import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import RedisConfig, get_settings


logger = logging.getLogger(__name__)


class RedisManager:
    """
    Redis connection manager.
    
    Supports:
    - Single Redis node
    - Redis Cluster
    
    Provides graceful degradation when Redis is unavailable.
    """
    
    def __init__(self, config: Optional[RedisConfig] = None):
        """
        Initialize Redis manager.
        
        Args:
            config: Redis configuration. If None, loads from settings.
        """
        self._config = config
        self._client: Optional[Redis] = None
        self._available = False
    
    @property
    def config(self) -> RedisConfig:
        """Get Redis configuration."""
        if self._config is None:
            self._config = get_settings().redis
        return self._config
    
    @property
    def is_enabled(self) -> bool:
        """Check if Redis is enabled."""
        return self.config.enabled
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._available and self._client is not None
    
    async def connect(self) -> bool:
        """
        Connect to Redis.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.is_enabled:
            logger.info("Redis is disabled in configuration")
            return False
        
        try:
            if self.config.mode == "cluster":
                self._client = redis.RedisCluster(
                    startup_nodes=[
                        {"host": node.host, "port": node.port}
                        for node in self.config.cluster.nodes
                    ],
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    retry_on_timeout=self.config.retry_on_timeout,
                    max_connections=self.config.max_connections,
                    decode_responses=True,
                )
                # Test connection
                await self._client.ping()
            else:
                self._client = redis.Redis(
                    host=self.config.single.host,
                    port=self.config.single.port,
                    password=self.config.single.password or None,
                    db=self.config.single.db,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    retry_on_timeout=self.config.retry_on_timeout,
                    max_connections=self.config.max_connections,
                    decode_responses=True,
                )
                # Test connection
                await self._client.ping()
            
            self._available = True
            logger.info(f"Redis connected successfully in {self.config.mode} mode")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Continuing without Redis.")
            self._available = False
            self._client = None
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None
            self._available = False
            logger.info("Redis disconnected")
    
    async def ping(self) -> bool:
        """
        Ping Redis server.
        
        Returns:
            True if Redis is available, False otherwise
        """
        if not self._client:
            return False
        try:
            return await self._client.ping()
        except Exception:
            return False
    
    def client(self) -> Optional[Redis]:
        """
        Get Redis client.
        
        Returns:
            Redis client or None if not available
        """
        return self._client
    
    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[Optional[Redis], None]:
        """
        Context manager for using Redis client.
        
        Usage:
            async with redis_manager.get_client() as redis:
                if redis:
                    await redis.set("key", "value")
        
        Yields:
            Redis client or None if not available
        """
        if not self.is_available or not self._client:
            yield None
            return
        
        try:
            yield self._client
        except Exception as e:
            logger.error(f"Redis operation failed: {e}")
            raise


# Global Redis manager instance
_redis_manager: Optional[RedisManager] = None


def get_redis_manager() -> RedisManager:
    """
    Get global Redis manager instance.
    
    Returns:
        RedisManager instance
    """
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager


async def get_redis() -> Optional[Redis]:
    """
    FastAPI dependency for getting Redis client.
    
    Returns Redis client if available, None otherwise.
    
    Usage:
        @app.get("/cache")
        async def get_cache(redis: Redis = Depends(get_redis)):
            if redis:
                value = await redis.get("key")
            ...
    """
    manager = get_redis_manager()
    if not manager.is_available:
        return None
    return manager.client()


# Convenience function for direct Redis operations
async def redis_get(key: str, default: Any = None) -> Any:
    """
    Get value from Redis.
    
    Args:
        key: Redis key
        default: Default value if key doesn't exist or Redis unavailable
        
    Returns:
        Cached value or default
    """
    async with get_redis_manager().get_client() as redis:
        if redis is None:
            return default
        try:
            value = await redis.get(key)
            return value if value is not None else default
        except Exception as e:
            logger.error(f"Redis get failed for key {key}: {e}")
            return default


async def redis_set(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """
    Set value in Redis.
    
    Args:
        key: Redis key
        value: Value to store
        expire: Expiration time in seconds
        
    Returns:
        True if successful, False otherwise
    """
    async with get_redis_manager().get_client() as redis:
        if redis is None:
            return False
        try:
            await redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis set failed for key {key}: {e}")
            return False


async def redis_delete(key: str) -> bool:
    """
    Delete key from Redis.
    
    Args:
        key: Redis key
        
    Returns:
        True if successful, False otherwise
    """
    async with get_redis_manager().get_client() as redis:
        if redis is None:
            return False
        try:
            await redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return False
