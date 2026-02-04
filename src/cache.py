"""
Redis Cache for Session Management
Fast in-memory caching for conversation context
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis-based caching with fallback to in-memory"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2
            )
            self.redis_client.ping()
            logger.info("✅ Redis connected")
        except:
            logger.warning("⚠️  Redis not available, using memory cache")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Dict]:
        """Get value from cache"""
        # Try Redis first
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except:
                pass
        
        # Fallback to memory
        return self.memory_cache.get(key)
    
    def set(self, key: str, value: Dict, ttl: int = 3600):
        """Set value in cache"""
        # Try Redis
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return
            except:
                pass
        
        # Fallback to memory
        self.memory_cache[key] = value
    
    def delete(self, key: str):
        """Delete from cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass
        
        self.memory_cache.pop(key, None)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.redis_client:
            try:
                return self.redis_client.exists(key) > 0
            except:
                pass
        
        return key in self.memory_cache

# Global cache instance
cache = RedisCache()
