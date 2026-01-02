"""Redis-based caching service for UnoBot."""
import json
import time
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta

import aioredis
from fastapi import HTTPException, status

from src.core.config import settings


class CacheService:
    """Redis-based caching service with TTL support."""

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_url = settings.redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            await self.redis.ping()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Redis connection failed: {e}"
            )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            # Serialize value to JSON
            serialized_value = json.dumps(value, default=str)

            if ttl:
                await self.redis.setex(key, ttl, serialized_value)
            else:
                await self.redis.set(key, serialized_value)

            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis:
            await self.connect()

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            result = await self.redis.expire(key, ttl)
            return result > 0
        except Exception as e:
            print(f"Cache expire error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, or -1 if key doesn't exist, -2 if no expiration
        """
        if not self.redis:
            await self.connect()

        try:
            return await self.redis.ttl(key)
        except Exception as e:
            print(f"Cache TTL error: {e}")
            return -1

    async def keys(self, pattern: str) -> List[str]:
        """
        Get all keys matching a pattern.

        Args:
            pattern: Redis pattern (e.g., "session:*")

        Returns:
            List of matching keys
        """
        if not self.redis:
            await self.connect()

        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            print(f"Cache keys error: {e}")
            return []

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Redis pattern (e.g., "session:*")

        Returns:
            Number of deleted keys
        """
        if not self.redis:
            await self.connect()

        try:
            keys = await self.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to increment by (default: 1)

        Returns:
            New value after increment
        """
        if not self.redis:
            await self.connect()

        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0

    async def set_hash(self, key: str, mapping: Dict[str, Any]) -> bool:
        """
        Set multiple fields in a hash.

        Args:
            key: Hash key
            mapping: Dictionary of field-value pairs

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            # Serialize values to JSON
            serialized_mapping = {
                field: json.dumps(value, default=str)
                for field, value in mapping.items()
            }
            await self.redis.hset(key, mapping=serialized_mapping)
            return True
        except Exception as e:
            print(f"Cache set hash error: {e}")
            return False

    async def get_hash(self, key: str, field: Optional[str] = None) -> Union[Dict[str, Any], Any, None]:
        """
        Get fields from a hash.

        Args:
            key: Hash key
            field: Specific field to get (optional)

        Returns:
            If field is specified: field value or None
            If field is None: entire hash as dictionary
        """
        if not self.redis:
            await self.connect()

        try:
            if field:
                value = await self.redis.hget(key, field)
                if value:
                    return json.loads(value)
                return None
            else:
                values = await self.redis.hgetall(key)
                return {
                    field: json.loads(value)
                    for field, value in values.items()
                }
        except Exception as e:
            print(f"Cache get hash error: {e}")
            return None if field else {}

    async def delete_hash_field(self, key: str, field: str) -> bool:
        """
        Delete a field from a hash.

        Args:
            key: Hash key
            field: Field to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            result = await self.redis.hdel(key, field)
            return result > 0
        except Exception as e:
            print(f"Cache delete hash field error: {e}")
            return False


# Global cache service instance
cache_service = CacheService()


def get_cache_service() -> CacheService:
    """Get cache service instance."""
    return cache_service


# Cache key prefixes for different data types
CACHE_PREFIXES = {
    "session": "session:",
    "expert": "expert:",
    "booking": "booking:",
    "rate_limit": "rate_limit:",
    "api_response": "api:",
    "ai_response": "ai:",
}


# Convenience functions for common cache operations

async def cache_session_data(
    session_id: str,
    data: Dict[str, Any],
    ttl: int = 86400 * 7  # 7 days
) -> bool:
    """Cache session data."""
    key = f"{CACHE_PREFIXES['session']}{session_id}"
    return await cache_service.set(key, data, ttl)


async def get_cached_session_data(session_id: str) -> Optional[Dict[str, Any]]:
    """Get cached session data."""
    key = f"{CACHE_PREFIXES['session']}{session_id}"
    return await cache_service.get(key)


async def cache_expert_data(
    expert_id: str,
    data: Dict[str, Any],
    ttl: int = 3600  # 1 hour
) -> bool:
    """Cache expert data."""
    key = f"{CACHE_PREFIXES['expert']}{expert_id}"
    return await cache_service.set(key, data, ttl)


async def get_cached_expert_data(expert_id: str) -> Optional[Dict[str, Any]]:
    """Get cached expert data."""
    key = f"{CACHE_PREFIXES['expert']}{expert_id}"
    return await cache_service.get(key)


async def cache_api_response(
    endpoint: str,
    params: Dict[str, Any],
    response: Any,
    ttl: int = 300  # 5 minutes
) -> bool:
    """Cache API response."""
    import hashlib
    params_str = json.dumps(params, sort_keys=True)
    cache_key = hashlib.md5(f"{endpoint}:{params_str}".encode()).hexdigest()
    key = f"{CACHE_PREFIXES['api_response']}{cache_key}"
    return await cache_service.set(key, response, ttl)


async def get_cached_api_response(
    endpoint: str,
    params: Dict[str, Any]
) -> Optional[Any]:
    """Get cached API response."""
    import hashlib
    params_str = json.dumps(params, sort_keys=True)
    cache_key = hashlib.md5(f"{endpoint}:{params_str}".encode()).hexdigest()
    key = f"{CACHE_PREFIXES['api_response']}{cache_key}"
    return await cache_service.get(key)


async def cache_ai_response(
    prompt_hash: str,
    response: Any,
    ttl: int = 3600  # 1 hour
) -> bool:
    """Cache AI response."""
    key = f"{CACHE_PREFIXES['ai_response']}{prompt_hash}"
    return await cache_service.set(key, response, ttl)


async def get_cached_ai_response(prompt_hash: str) -> Optional[Any]:
    """Get cached AI response."""
    key = f"{CACHE_PREFIXES['ai_response']}{prompt_hash}"
    return await cache_service.get(key)


async def increment_rate_limit(identifier: str, window_seconds: int = 60) -> int:
    """Increment rate limit counter."""
    key = f"{CACHE_PREFIXES['rate_limit']}{identifier}"
    current = await cache_service.increment(key)

    # Set expiration if this is the first increment
    if current == 1:
        await cache_service.expire(key, window_seconds)

    return current


async def clear_expired_cache(pattern: str) -> int:
    """Clear expired cache entries."""
    keys = await cache_service.keys(pattern)
    cleared = 0

    for key in keys:
        ttl = await cache_service.ttl(key)
        if ttl == -1:  # Key doesn't exist (expired)
            await cache_service.delete(key)
            cleared += 1
        elif ttl == -2:  # No expiration set
            # Set default expiration
            await cache_service.expire(key, 3600)

    return cleared


__all__ = [
    "CacheService",
    "get_cache_service",
    "cache_service",
    "cache_session_data",
    "get_cached_session_data",
    "cache_expert_data",
    "get_cached_expert_data",
    "cache_api_response",
    "get_cached_api_response",
    "cache_ai_response",
    "get_cached_ai_response",
    "increment_rate_limit",
    "clear_expired_cache",
    "CACHE_PREFIXES",
]