"""Redis cache wrapper for Social Trends Harvester."""

import hashlib
import json
import logging
from typing import Any, Optional

from .config import settings

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False


class CacheManager:
    """Redis cache manager with fallback to in-memory cache."""

    def __init__(self):
        """Initialize cache manager."""
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: dict[str, Any] = {}
        self.enabled = False

    async def initialize(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE or not settings.REDIS_URL:
            logger.info("Redis not available or not configured, using memory cache")
            self.enabled = True
            return

        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, falling back to memory cache")
            self.redis_client = None
            self.enabled = True

    async def cleanup(self):
        """Cleanup cache connections."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    def _generate_key(self, namespace: str, params: dict[str, Any]) -> str:
        """Generate cache key from namespace and parameters."""
        # Sort params for consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        key_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
        return f"sth:{namespace}:{key_hash}"

    async def get(self, namespace: str, params: dict[str, Any]) -> Optional[Any]:
        """Get cached value."""
        if not self.enabled:
            return None

        key = self._generate_key(namespace, params)

        try:
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Memory cache
                if key in self.memory_cache:
                    return self.memory_cache[key]
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")

        return None

    async def set(self, namespace: str, params: dict[str, Any], value: Any) -> bool:
        """Set cached value."""
        if not self.enabled:
            return False

        key = self._generate_key(namespace, params)

        try:
            serialized_value = json.dumps(value)

            if self.redis_client:
                await self.redis_client.setex(key, settings.CACHE_TTL_S, serialized_value)
            else:
                # Memory cache (no TTL for simplicity)
                self.memory_cache[key] = value

            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def delete(self, namespace: str, params: dict[str, Any]) -> bool:
        """Delete cached value."""
        if not self.enabled:
            return False

        key = self._generate_key(namespace, params)

        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            else:
                # Memory cache
                self.memory_cache.pop(key, None)

            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    async def clear_all(self) -> bool:
        """Clear all cache entries."""
        if not self.enabled:
            return False

        try:
            if self.redis_client:
                # Delete all keys with our prefix
                keys = await self.redis_client.keys("sth:*")
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                # Memory cache
                self.memory_cache.clear()

            logger.info("Cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "enabled": self.enabled,
            "backend": "redis" if self.redis_client else "memory",
            "ttl_seconds": settings.CACHE_TTL_S,
        }

        try:
            if self.redis_client:
                info = await self.redis_client.info()
                stats.update(
                    {
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory": info.get("used_memory_human", "unknown"),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                    }
                )
            else:
                stats.update({"memory_keys": len(self.memory_cache)})
        except Exception as e:
            logger.warning(f"Error getting cache stats: {e}")

        return stats


# Global cache manager instance
cache_manager = CacheManager()
