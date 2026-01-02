"""Redis-based caching service for UnoBot with fallback to in-memory cache."""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING

from src.core.config import settings

if TYPE_CHECKING:
    import redis.asyncio as redis_async

# Try to import Redis, fallback to in-memory if not available
try:
    import redis.asyncio as redis_async
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis_async = None  # type: ignore


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        """Initialize in-memory cache."""
        self.cache: dict[str, dict[str, Any]] = {}
        self.ttl_tasks: list[asyncio.Task] = []

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> bool:
        """Set a value in cache."""
        try:
            self.cache[key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl) if ttl else None
            }

            # Schedule cleanup if TTL is set
            if ttl:
                task = asyncio.create_task(self._schedule_cleanup(key, ttl))
                self.ttl_tasks.append(task)

            return True
        except Exception:
            return False

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if entry['expires_at'] and datetime.now() > entry['expires_at']:
            await self.delete(key)
            return None

        return entry['value']

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if key not in self.cache:
            return False

        entry = self.cache[key]
        if entry['expires_at'] and datetime.now() > entry['expires_at']:
            await self.delete(key)
            return False

        return True

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        if key in self.cache:
            self.cache[key]['expires_at'] = datetime.now() + timedelta(seconds=ttl)
            return True
        return False

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key."""
        if key not in self.cache:
            return -1

        entry = self.cache[key]
        if entry['expires_at']:
            remaining = (entry['expires_at'] - datetime.now()).total_seconds()
            return max(0, int(remaining))
        return -2  # No expiration

    async def keys(self, pattern: str) -> list[str]:
        """Get all keys matching a pattern."""
        import fnmatch
        return [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        keys_to_delete = await self.keys(pattern)
        deleted = 0
        for key in keys_to_delete:
            if await self.delete(key):
                deleted += 1
        return deleted

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache."""
        current = await self.get(key)
        if current is None:
            current = 0

        new_value = current + amount
        await self.set(key, new_value)
        return new_value

    async def set_hash(self, key: str, mapping: dict[str, Any]) -> bool:
        """Set multiple fields in a hash."""
        return await self.set(key, mapping)

    async def get_hash(self, key: str, field: str | None = None) -> dict[str, Any] | Any | None:
        """Get fields from a hash."""
        value = await self.get(key)
        if value is None:
            return None

        if field:
            return value.get(field) if isinstance(value, dict) else None
        return value if isinstance(value, dict) else {}

    async def delete_hash_field(self, key: str, field: str) -> bool:
        """Delete a field from a hash."""
        value = await self.get(key)
        if isinstance(value, dict) and field in value:
            del value[field]
            await self.set(key, value)
            return True
        return False

    async def _schedule_cleanup(self, key: str, ttl: int):
        """Schedule cleanup of a key after TTL."""
        await asyncio.sleep(ttl)
        await self.delete(key)


class CacheService:
    """Redis-based caching service with TTL support and fallback to in-memory."""

    def __init__(self):
        """Initialize cache service with Redis or fallback."""
        self.redis_url = settings.redis_url
        self.redis: Any | None = None
        self.in_memory_cache: InMemoryCache = InMemoryCache()  # Always initialize
        self.use_redis: bool = False

    async def connect(self) -> None:
        """Connect to Redis or initialize in-memory cache."""
        if REDIS_AVAILABLE:
            try:
                self.redis = redis_async.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                await self.redis.ping()
                self.use_redis = True
                return
            except Exception:
                pass

        # Fallback to in-memory cache (already initialized)
        self.use_redis = False

    async def disconnect(self) -> None:
        """Disconnect from cache service."""
        if self.use_redis and self.redis:
            await self.redis.close()
        # In-memory cache doesn't need explicit disconnection

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> bool:
        """Set a value in cache."""
        if self.use_redis and self.redis:
            try:
                # Serialize value to JSON
                serialized_value = json.dumps(value, default=str)

                if ttl:
                    await self.redis.setex(key, ttl, serialized_value)
                else:
                    await self.redis.set(key, serialized_value)

                return True
            except Exception:
                return False
        else:
            return await self.in_memory_cache.set(key, value, ttl)

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        if self.use_redis and self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception:
                return None
        else:
            return await self.in_memory_cache.get(key)

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if self.use_redis and self.redis:
            try:
                result = await self.redis.delete(key)
                return bool(result > 0)
            except Exception:
                return False
        else:
            return await self.in_memory_cache.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if self.use_redis and self.redis:
            try:
                result = await self.redis.exists(key)
                return bool(result > 0)
            except Exception:
                return False
        else:
            return await self.in_memory_cache.exists(key)

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        if self.use_redis and self.redis:
            try:
                result = await self.redis.expire(key, ttl)
                return bool(result > 0)
            except Exception:
                return False
        else:
            return await self.in_memory_cache.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key."""
        if self.use_redis and self.redis:
            try:
                return int(await self.redis.ttl(key))
            except Exception:
                return -1
        else:
            return await self.in_memory_cache.ttl(key)

    async def keys(self, pattern: str) -> list[str]:
        """Get all keys matching a pattern."""
        if self.use_redis and self.redis:
            try:
                result = await self.redis.keys(pattern)
                return list(result) if result else []
            except Exception:
                return []
        else:
            return await self.in_memory_cache.keys(pattern)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if self.use_redis and self.redis:
            try:
                keys = await self.keys(pattern)
                if keys:
                    result = await self.redis.delete(*keys)
                    return int(result)
                return 0
            except Exception:
                return 0
        else:
            return await self.in_memory_cache.delete_pattern(pattern)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache."""
        if self.use_redis and self.redis:
            try:
                result = await self.redis.incr(key, amount)
                return int(result)
            except Exception:
                return 0
        else:
            return await self.in_memory_cache.increment(key, amount)

    async def set_hash(self, key: str, mapping: dict[str, Any]) -> bool:
        """Set multiple fields in a hash."""
        if self.use_redis and self.redis:
            try:
                # Serialize values to JSON
                serialized_mapping = {
                    field: json.dumps(value, default=str)
                    for field, value in mapping.items()
                }
                await self.redis.hset(key, mapping=serialized_mapping)
                return True
            except Exception:
                return False
        else:
            return await self.in_memory_cache.set_hash(key, mapping)

    async def get_hash(self, key: str, field: str | None = None) -> dict[str, Any] | Any | None:
        """Get fields from a hash."""
        if self.use_redis and self.redis:
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
            except Exception:
                return None if field else {}
        else:
            return await self.in_memory_cache.get_hash(key, field)

    async def delete_hash_field(self, key: str, field: str) -> bool:
        """Delete a field from a hash."""
        if self.use_redis and self.redis:
            try:
                result = await self.redis.hdel(key, field)
                return bool(result > 0)
            except Exception:
                return False
        else:
            return await self.in_memory_cache.delete_hash_field(key, field)


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
    data: dict[str, Any],
    ttl: int = 86400 * 7  # 7 days
) -> bool:
    """Cache session data."""
    key = f"{CACHE_PREFIXES['session']}{session_id}"
    return await cache_service.set(key, data, ttl)


async def get_cached_session_data(session_id: str) -> dict[str, Any] | None:
    """Get cached session data."""
    key = f"{CACHE_PREFIXES['session']}{session_id}"
    return await cache_service.get(key)


async def delete_cached_session_data(session_id: str) -> bool:
    """Delete cached session data."""
    key = f"{CACHE_PREFIXES['session']}{session_id}"
    return await cache_service.delete(key)


async def cache_expert_data(
    expert_id: str,
    data: dict[str, Any],
    ttl: int = 3600  # 1 hour
) -> bool:
    """Cache expert data."""
    key = f"{CACHE_PREFIXES['expert']}{expert_id}"
    return await cache_service.set(key, data, ttl)


async def get_cached_expert_data(expert_id: str) -> dict[str, Any] | None:
    """Get cached expert data."""
    key = f"{CACHE_PREFIXES['expert']}{expert_id}"
    return await cache_service.get(key)


async def cache_api_response(
    endpoint: str,
    params: dict[str, Any],
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
    params: dict[str, Any]
) -> Any | None:
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


async def get_cached_ai_response(prompt_hash: str) -> Any | None:
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
    "delete_cached_session_data",
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
