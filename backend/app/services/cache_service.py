import json
from typing import Any, Optional, Dict
import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)

class CacheService:
    """Centralized caching service for Enterprise AI performance."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = False
        
    async def connect(self):
        """Initialize connection to Redis."""
        try:
            # Check if REDIS_URL is configured
            redis_url = getattr(settings, "REDIS_URL", None)
            if not redis_url:
                logger.warning("REDIS_URL not configured. Caching disabled.")
                return
            
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            await self.redis_client.ping()
            self.enabled = True
            logger.info("Successfully connected to Redis for caching.")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self.enabled = False

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        if not self.enabled or not self.redis_client:
            return None
            
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error reading from cache: {key}", error=str(e))
            
        return None

    async def set(self, key: str, value: Any, expire_seconds: int = 3600):
        """Store a value in cache with expiration."""
        if not self.enabled or not self.redis_client:
            return
            
        try:
            data = json.dumps(value)
            await self.redis_client.set(key, data, ex=expire_seconds)
        except Exception as e:
            logger.error(f"Error writing to cache: {key}", error=str(e))

    async def delete(self, key: str):
        """Remove a value from cache."""
        if not self.enabled or not self.redis_client:
            return
            
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting from cache: {key}", error=str(e))

# Global instance
cache = CacheService()
