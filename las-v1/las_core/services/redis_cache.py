"""
Redis Cache Service - High-performance caching with Redis.
"""

import redis
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import os

class RedisCache:
    """Redis-based caching service for improved performance."""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Optional password
        """
        # Get from environment if not provided
        host = os.getenv('REDIS_HOST', host)
        port = int(os.getenv('REDIS_PORT', port))
        password = os.getenv('REDIS_PASSWORD', password)
        
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis.ping()
            self.available = True
        except (redis.ConnectionError, redis.TimeoutError):
            # Redis not available, cache will be no-op
            self.redis = None
            self.available = False
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            prefix: Key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            MD5 hash of serialized arguments
        """
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.available:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set cached value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        if not self.available:
            return
        
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception:
            pass
    
    def delete(self, key: str):
        """Delete cached key."""
        if not self.available:
            return
        
        try:
            self.redis.delete(key)
        except Exception:
            pass
    
    def invalidate(self, pattern: str):
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "user:*")
        """
        if not self.available:
            return
        
        try:
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
        except Exception:
            pass
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.available:
            return {"available": False}
        
        try:
            info = self.redis.info('stats')
            return {
                "available": True,
                "hits": info.get('keyspace_hits', 0),
                "misses": info.get('keyspace_misses', 0),
                "hit_rate": self._calculate_hit_rate(info),
                "keys": self.redis.dbsize()
            }
        except Exception:
            return {"available": False}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# Decorator for caching function results
def cached(ttl: int = 3600, prefix: str = "cache"):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        prefix: Cache key prefix
        
    Example:
        @cached(ttl=1800, prefix="user")
        def get_user(user_id: int):
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_redis_cache()
            
            # Generate cache key
            key = cache.cache_key(prefix, *args, **kwargs)
            
            # Try cache first
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

# Singleton instance
_redis_cache: Optional[RedisCache] = None

def get_redis_cache() -> RedisCache:
    """Get or create Redis cache singleton."""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
