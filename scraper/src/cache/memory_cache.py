import time
from typing import Any, Optional, Dict
from collections import OrderedDict

class MemoryCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired."""
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        if entry['expires_at'] < time.time():
            self.delete(key)
            return None
            
        # Move to end to implement LRU
        self.cache.move_to_end(key)
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with expiration time."""
        # Enforce max size limit using LRU
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
            
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
        
        # Move to end to implement LRU
        self.cache.move_to_end(key)
    
    def delete(self, key: str) -> None:
        """Remove a key from cache."""
        self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self.cache.clear()
    
    def cleanup(self) -> None:
        """Remove all expired entries."""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry['expires_at'] < now
        ]
        for key in expired_keys:
            self.delete(key)
