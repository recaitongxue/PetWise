"""
Cache Management Module
Provides in-memory caching with TTL support
"""
import time
import hashlib
import json
from typing import Any, Optional, Dict
from threading import Lock
from collections import OrderedDict

from config import Config
from utils import setup_logging

logger = setup_logging(Config.LOG_LEVEL)

class CacheEntry:
    """Cache entry with TTL"""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return time.time() - self.created_at > self.ttl
    
    def get_age(self) -> float:
        """Get entry age in seconds"""
        return time.time() - self.created_at

class Cache:
    """Thread-safe in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = None, ttl: int = None):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of entries
            ttl: Default TTL in seconds
        """
        self.max_size = max_size or Config.CACHE_MAX_SIZE
        self.default_ttl = ttl or Config.CACHE_TTL
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        
        logger.info(f"Cache initialized with max_size={self.max_size}, ttl={self.default_ttl}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            self._cache.move_to_end(key)
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        with self._lock:
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_oldest()
            
            entry_ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, entry_ttl)
            self._cache.move_to_end(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed and was deleted
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("Cache cleared")
    
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "default_ttl": self.default_ttl
            }
    
    def memoize(self, ttl: Optional[int] = None):
        """
        Decorator for memoizing function results
        
        Args:
            ttl: TTL in seconds (uses default if None)
            
        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, *args, **kwargs)
                cached = self.get(key)
                
                if cached is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached
                
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                logger.debug(f"Cache miss for {func.__name__}, result cached")
                
                return result
            
            return wrapper
        return decorator

class ModelCache:
    """Specialized cache for AI models"""
    
    def __init__(self):
        self.cache = Cache(ttl=Config.MODELS_CACHE_TTL)
        self._models_key = "available_models"
    
    def get_models(self) -> Optional[list]:
        """Get cached models list"""
        return self.cache.get(self._models_key)
    
    def set_models(self, models: list):
        """Cache models list"""
        self.cache.set(self._models_key, models)
    
    def invalidate_models(self):
        """Invalidate cached models"""
        self.cache.delete(self._models_key)
        logger.info("Models cache invalidated")

global_cache = None
model_cache = None

def get_cache() -> Cache:
    """Get global cache instance"""
    global global_cache
    if global_cache is None:
        global_cache = Cache()
    return global_cache

def get_model_cache() -> ModelCache:
    """Get model cache instance"""
    global model_cache
    if model_cache is None:
        model_cache = ModelCache()
    return model_cache

def init_cache():
    """Initialize cache instances"""
    global global_cache, model_cache
    
    if not Config.CACHE_ENABLED:
        logger.info("Cache is disabled")
        return
    
    global_cache = Cache()
    model_cache = ModelCache()
    logger.info("Cache initialized successfully")