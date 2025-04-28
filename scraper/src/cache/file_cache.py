import os
import json
import time
from typing import Any, Optional
from pathlib import Path

class FileCache:
    def __init__(self, cache_dir: str = "cache"):
        """Initialize file cache with specified directory."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        # Use hash of key to avoid filesystem issues with long/special characters
        hashed_key = str(hash(key))
        return self.cache_dir / f"{hashed_key}.json"
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            if not cache_path.exists():
                return None
                
            with cache_path.open('r') as f:
                data = json.load(f)
                
            # Check if data has expired
            if data['expires_at'] < time.time():
                self.delete(key)
                return None
                
            return data['value']
        except (json.JSONDecodeError, KeyError, IOError):
            return None
            
    def set(self, key: str, value: Any, ttl: int = 86400) -> None:
        """Set value in file cache with expiration."""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'value': value,
                'expires_at': time.time() + ttl
            }
            
            with cache_path.open('w') as f:
                json.dump(data, f)
        except (IOError, TypeError):
            # Log error but don't raise - cache failures shouldn't break the app
            pass
            
    def delete(self, key: str) -> None:
        """Remove a key from file cache."""
        cache_path = self._get_cache_path(key)
        try:
            cache_path.unlink(missing_ok=True)
        except IOError:
            pass
            
    def clear(self) -> None:
        """Clear all entries from file cache."""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
        except IOError:
            pass
            
    def cleanup_expired(self) -> None:
        """Remove all expired cache files."""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    with cache_file.open('r') as f:
                        data = json.load(f)
                    if data['expires_at'] < time.time():
                        cache_file.unlink()
                except (json.JSONDecodeError, KeyError, IOError):
                    # Delete corrupt cache files
                    cache_file.unlink()
        except IOError:
            pass
