"""
Unit tests for cache module
"""
import pytest
import time
from cache import Cache, get_cache, init_cache


class TestCache:
    """Tests for Cache class"""

    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = Cache(max_size=50, ttl=60)
        assert cache.max_size == 50
        assert cache.default_ttl == 60

    def test_cache_set_get(self):
        """Test basic cache operations"""
        cache = Cache()
        
        # Set a value
        cache.set("test_key", "test_value")
        
        # Get the value
        result = cache.get("test_key")
        assert result == "test_value"

    def test_cache_expiration(self):
        """Test cache TTL expiration"""
        cache = Cache(ttl=1)  # 1 second TTL
        
        cache.set("temp_key", "temp_value")
        assert cache.get("temp_key") == "temp_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        result = cache.get("temp_key")
        assert result is None

    def test_cache_eviction(self):
        """Test LRU eviction"""
        cache = Cache(max_size=3)
        
        # Add 4 items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1
        
        # key1 should be evicted
        assert cache.get("key1") is None
        # Others should still be there
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_cache_delete(self):
        """Test cache deletion"""
        cache = Cache()
        cache.set("to_delete", "value")
        
        assert cache.get("to_delete") == "value"
        cache.delete("to_delete")
        assert cache.get("to_delete") is None

    def test_cache_clear(self):
        """Test cache clear"""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        assert stats["size"] == 2
        
        cache.clear()
        
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert cache.get("key1") is None

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = Cache()
        
        # Miss
        cache.get("nonexistent")
        
        # Hit
        cache.set("key", "value")
        cache.get("key")
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_global_cache(self):
        """Test global cache instance"""
        init_cache()
        cache = get_cache()
        
        assert cache is not None
        cache.set("global_key", "global_value")
        
        # Get from same instance
        cache2 = get_cache()
        assert cache2.get("global_key") == "global_value"