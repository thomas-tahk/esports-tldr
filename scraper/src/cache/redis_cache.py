from typing import Any, Optional
import redis
import json
from datetime import timedelta

class RedisCache:
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection."""
        if redis_url:
            self.redis = redis.from_url(redis_url)
        else:
            self.redis = redis.Redis(host='localhost', port=6379, db=0)
            
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.RedisError, json.JSONDecodeError):
            return None
            
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis cache with expiration."""
        try:
            serialized = json.dumps(value)
            self.redis.setex(
                name=key,
                time=timedelta(seconds=ttl),
                value=serialized
            )
        except (redis.RedisError, TypeError):
            # Log error but don't raise - cache failures shouldn't break the app
            pass
            
    def delete(self, key: str) -> None:
        """Remove a key from Redis cache."""
        try:
            self.redis.delete(key)
        except redis.RedisError:
            pass
            
    def clear(self) -> None:
        """Clear all entries from Redis cache."""
        try:
            self.redis.flushdb()
        except redis.RedisError:
            pass
            
    def ping(self) -> bool:
        """Check if Redis connection is alive."""
        try:
            return self.redis.ping()
        except redis.RedisError:
            return False
