"""
Caching utilities.

Provides caching decorators and helpers for function results.
"""

import functools
import hashlib
import json
from typing import Any, Callable, Optional
from datetime import datetime, timedelta

# In-memory cache storage
_cache: dict = {}


def _make_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    # Convert args and kwargs to a hashable string
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items()),
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(
    expire_seconds: int = 300,
    key_prefix: str = "",
) -> Callable:
    """
    Cache decorator for function results.
    
    Args:
        expire_seconds: Cache expiration time in seconds
        key_prefix: Prefix for cache keys
        
    Returns:
        Decorated function
        
    Example:
        @cache_result(expire_seconds=60)
        def get_user(user_id: int):
            # Expensive database query
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{_make_cache_key(*args, **kwargs)}"
            
            # Check if cached
            if cache_key in _cache:
                cached_data, expire_time = _cache[cache_key]
                
                # Check if expired
                if datetime.now() < expire_time:
                    return cached_data
            
            # Call function and cache result
            result = func(*args, **kwargs)
            
            expire_time = datetime.now() + timedelta(seconds=expire_seconds)
            _cache[cache_key] = (result, expire_time)
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: _clear_function_cache(func.__name__, key_prefix)
        wrapper.cache_info = lambda: _get_cache_info(cache_key, key_prefix)
        
        return wrapper
    return decorator


def _clear_function_cache(func_name: str, key_prefix: str) -> int:
    """Clear cache for a specific function."""
    prefix = f"{key_prefix}:{func_name}:"
    keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
    
    for key in keys_to_delete:
        del _cache[key]
    
    return len(keys_to_delete)


def _get_cache_info(func_name: str, key_prefix: str) -> dict:
    """Get cache information for a function."""
    prefix = f"{key_prefix}:{func_name}:"
    
    cache_entries = {
        k: {
            'expire_time': v[1].isoformat(),
            'is_expired': datetime.now() >= v[1],
        }
        for k, v in _cache.items()
        if k.startswith(prefix)
    }
    
    return {
        'function': func_name,
        'total_entries': len(cache_entries),
        'entries': cache_entries,
    }


def clear_cache(prefix: Optional[str] = None) -> int:
    """
    Clear all cache or cache with specific prefix.
    
    Args:
        prefix: Optional prefix to clear (clears all if None)
        
    Returns:
        Number of entries cleared
    """
    global _cache
    
    if prefix is None:
        count = len(_cache)
        _cache = {}
        return count
    
    keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
    
    for key in keys_to_delete:
        del _cache[key]
    
    return len(keys_to_delete)


def get_cache_stats() -> dict:
    """Get overall cache statistics."""
    total_entries = len(_cache)
    expired_entries = 0
    active_entries = 0
    
    now = datetime.now()
    for _, expire_time in _cache.values():
        if now >= expire_time:
            expired_entries += 1
        else:
            active_entries += 1
    
    return {
        'total_entries': total_entries,
        'active_entries': active_entries,
        'expired_entries': expired_entries,
    }


# Redis-based caching (if Redis is available)
async def redis_cache_result(
    expire_seconds: int = 300,
    key_prefix: str = "cache",
):
    """
    Redis-based cache decorator.
    
    Requires Redis to be configured and available.
    
    Args:
        expire_seconds: Cache expiration time in seconds
        key_prefix: Prefix for cache keys
        
    Returns:
        Decorated function
    """
    from app.redis_client import get_redis_manager
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis_manager = get_redis_manager()
            
            if not redis_manager.is_available:
                # Fallback to function call if Redis unavailable
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{_make_cache_key(*args, **kwargs)}"
            
            redis = redis_manager.client()
            
            # Try to get from cache
            cached = await redis.get(cache_key)
            if cached:
                import pickle
                return pickle.loads(cached)
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            
            # Store in Redis
            import pickle
            await redis.setex(
                cache_key,
                expire_seconds,
                pickle.dumps(result),
            )
            
            return result
        
        return wrapper
    return decorator
