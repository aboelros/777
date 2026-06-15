"""
Advanced Caching Service
Redis-based caching layer with intelligent invalidation strategies.
"""
from typing import Dict, List, Any, Optional, Callable
import json
import hashlib
from datetime import timedelta
from redis import asyncio as aioredis
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class CacheService:
    """
    Advanced caching service with Redis backend.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: Optional[aioredis.Redis] = None
        self.default_ttl = 3600  # 1 hour
    
    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            logger.info("Cache service connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """Generate cache key."""
        return f"cache:{namespace}:{identifier}"
    
    async def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            namespace: Cache namespace (e.g., 'users', 'projects')
            identifier: Unique identifier
            
        Returns:
            Cached value or None
        """
        await self.connect()
        
        key = self._generate_key(namespace, identifier)
        value = await self.redis.get(key)
        
        if value:
            logger.debug("Cache hit", namespace=namespace, identifier=identifier)
            return json.loads(value)
        
        logger.debug("Cache miss", namespace=namespace, identifier=identifier)
        return None
    
    async def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set value in cache.
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            value: Value to cache
            ttl: Time to live in seconds
        """
        await self.connect()
        
        key = self._generate_key(namespace, identifier)
        ttl = ttl or self.default_ttl
        
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
        
        logger.debug(
            "Cache set",
            namespace=namespace,
            identifier=identifier,
            ttl=ttl
        )
    
    async def delete(self, namespace: str, identifier: str):
        """Delete value from cache."""
        await self.connect()
        
        key = self._generate_key(namespace, identifier)
        await self.redis.delete(key)
        
        logger.debug("Cache deleted", namespace=namespace, identifier=identifier)
    
    async def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., 'cache:users:*')
        """
        await self.connect()
        
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await self.redis.delete(*keys)
            logger.info("Cache invalidated", pattern=pattern, count=len(keys))
    
    async def cached(
        self,
        namespace: str,
        identifier: str,
        func: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Cache decorator pattern - get from cache or execute function.
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            func: Async function to execute if cache miss
            ttl: Time to live
            
        Returns:
            Cached or computed value
        """
        # Try cache first
        cached_value = await self.get(namespace, identifier)
        if cached_value is not None:
            return cached_value
        
        # Execute function
        value = await func()
        
        # Cache result
        await self.set(namespace, identifier, value, ttl)
        
        return value


class QueryCache:
    """
    Database query result caching with automatic invalidation.
    """
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def _generate_query_hash(self, query: str, params: Dict) -> str:
        """Generate hash for query + params."""
        query_str = f"{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    async def get_query_result(
        self,
        query: str,
        params: Dict,
        executor: Callable
    ) -> Any:
        """
        Get query result from cache or execute query.
        
        Args:
            query: SQL query string
            params: Query parameters
            executor: Async function to execute query
            
        Returns:
            Query result
        """
        query_hash = self._generate_query_hash(query, params)
        
        return await self.cache.cached(
            namespace='queries',
            identifier=query_hash,
            func=executor,
            ttl=300  # 5 minutes for queries
        )
    
    async def invalidate_table(self, table_name: str):
        """Invalidate all queries for a table."""
        # In production, maintain query-to-table mapping
        await self.cache.invalidate_pattern(f'cache:queries:*')
        logger.info("Table cache invalidated", table=table_name)


class CDNIntegration:
    """
    CDN integration for static assets and media files.
    """
    
    def __init__(self, cdn_url: Optional[str] = None):
        self.cdn_url = cdn_url or settings.CDN_URL or ''
        self.enabled = bool(self.cdn_url)
    
    def get_asset_url(self, asset_path: str) -> str:
        """
        Get CDN URL for asset.
        
        Args:
            asset_path: Relative asset path
            
        Returns:
            Full CDN URL or local path
        """
        if self.enabled:
            return f"{self.cdn_url}/{asset_path.lstrip('/')}"
        return asset_path
    
    def get_media_url(self, media_id: str, filename: str) -> str:
        """Get CDN URL for media file."""
        path = f"media/{media_id}/{filename}"
        return self.get_asset_url(path)


# Global cache instance
cache_service = CacheService()
query_cache = QueryCache(cache_service)
cdn = CDNIntegration()
