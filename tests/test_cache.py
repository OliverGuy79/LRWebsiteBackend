"""Tests for the cache service."""

import time
from app.services.cache_service import CacheService


def test_cache_set_and_get():
    """Test basic set and get operations."""
    cache = CacheService(default_ttl=60)
    
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_get_nonexistent():
    """Test getting a key that doesn't exist."""
    cache = CacheService(default_ttl=60)
    
    assert cache.get("nonexistent") is None


def test_cache_expiration():
    """Test that expired entries return None."""
    cache = CacheService(default_ttl=1)  # 1 second TTL
    
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    # Wait for expiration
    time.sleep(1.1)
    assert cache.get("key1") is None


def test_cache_delete():
    """Test deleting a key."""
    cache = CacheService(default_ttl=60)
    
    cache.set("key1", "value1")
    assert cache.delete("key1") is True
    assert cache.get("key1") is None
    assert cache.delete("key1") is False  # Already deleted


def test_cache_clear():
    """Test clearing all entries."""
    cache = CacheService(default_ttl=60)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_cache_custom_ttl():
    """Test setting a custom TTL for a specific entry."""
    cache = CacheService(default_ttl=60)
    
    cache.set("key1", "value1", ttl=1)  # 1 second TTL
    assert cache.get("key1") == "value1"
    
    time.sleep(1.1)
    assert cache.get("key1") is None
