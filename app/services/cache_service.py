"""Simple in-memory TTL cache service."""

import time
from typing import Any
from threading import Lock


class CacheEntry:
    """A single cache entry with value and expiration time."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = time.time() + ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at


class CacheService:
    """Thread-safe in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 600):
        """
        Initialize the cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 10 minutes)
        """
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Any | None:
        """
        Get a value from the cache.
        
        Returns None if key doesn't exist or has expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.value
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Optional TTL override in seconds
        """
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl or self._default_ttl)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Returns True if key existed, False otherwise.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns the number of entries removed.
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)


# Global cache instance
_cache: CacheService | None = None


def get_cache(ttl: int = 600) -> CacheService:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = CacheService(default_ttl=ttl)
    return _cache
