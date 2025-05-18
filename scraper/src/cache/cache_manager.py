import time
from typing import Any, Optional, Dict
from functools import wraps
import redis
import json
import os
from .memory_cache import MemoryCache
from .redis_cache import RedisCache
from .file_cache import FileCache

class CacheManager:
    def __init__(self, redis_url: Optional[str] = None, cache_dir: str = "cache"):
        # Initialize cache layers
        self.memory_cache = MemoryCache()
        self.redis_cache = RedisCache(redis_url) if redis_url else None
        self.file_cache = FileCache(cache_dir)
        
        # Default TTLs for different types of data (in seconds)
        self.ttls = {
            'tournament': 3600,  # 1 hour for tournament data
            'player': 7200,     # 2 hours for player data
            'static': 86400,    # 24 hours for static data
        }

    def get(self, key: str, data_type: str = 'static') -> Optional[Any]:
        """
        Get data from cache, trying each layer in order:
        1. Memory cache (fastest)
        2. Redis cache (if available)
        3. File cache (slowest)
        """
        # Try memory cache first
        data = self.memory_cache.get(key)
        if data is not None:
            return data

        # Try Redis if available
        if self.redis_cache:
            data = self.redis_cache.get(key)
            if data is not None:
                # Populate memory cache
                self.memory_cache.set(key, data, self.ttls[data_type])
                return data

        # Try file cache last
        data = self.file_cache.get(key)
        if data is not None:
            # Populate faster caches
            self.memory_cache.set(key, data, self.ttls[data_type])
            if self.redis_cache:
                self.redis_cache.set(key, data, self.ttls[data_type])
            return data

        return None

    def set(self, key: str, value: Any, data_type: str = 'static') -> None:
        """Set data in all cache layers."""
        ttl = self.ttls[data_type]
        
        # Set in memory cache
        self.memory_cache.set(key, value, ttl)
        
        # Set in Redis if available
        if self.redis_cache:
            self.redis_cache.set(key, value, ttl)
        
        # Set in file cache
        self.file_cache.set(key, value)

    def invalidate(self, key: str) -> None:
        """Invalidate a key from all cache layers."""
        self.memory_cache.delete(key)
        if self.redis_cache:
            self.redis_cache.delete(key)
        self.file_cache.delete(key)

    def clear_all(self) -> None:
        """Clear all cache layers."""
        self.memory_cache.clear()
        if self.redis_cache:
            self.redis_cache.clear()
        self.file_cache.clear()

    def warmup(self, data_dict: Dict[str, Any], data_type: str = 'static') -> None:
        """Warm up the cache with initial data."""
        for key, value in data_dict.items():
            self.set(key, value, data_type)

def cache_decorator(cache_manager: CacheManager, key_prefix: str, data_type: str = 'static'):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache_manager.get(cache_key, data_type)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, data_type)
            return result
        return wrapper
    return decorator
