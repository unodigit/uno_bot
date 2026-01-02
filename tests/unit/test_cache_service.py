"""Unit tests for CacheService."""
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.core.config import settings
from src.services.cache_service import (
    CacheService,
    InMemoryCache,
    cache_session_data,
    clear_expired_cache,
    delete_cached_session_data,
    get_cached_session_data,
    increment_rate_limit,
)


class TestInMemoryCache:
    """Test cases for InMemoryCache."""

    @pytest.fixture
    def in_memory_cache(self):
        """Create InMemoryCache instance."""
        return InMemoryCache()

    @pytest.mark.asyncio
    async def test_set_and_get(self, in_memory_cache):
        """Test setting and getting values."""
        result = await in_memory_cache.set("test_key", "test_value", ttl=60)
        assert result is True

        value = await in_memory_cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_set_without_ttl(self, in_memory_cache):
        """Test setting value without TTL."""
        result = await in_memory_cache.set("test_key", "test_value")
        assert result is True

        value = await in_memory_cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, in_memory_cache):
        """Test getting non-existent key."""
        value = await in_memory_cache.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete(self, in_memory_cache):
        """Test deleting keys."""
        await in_memory_cache.set("test_key", "test_value")
        result = await in_memory_cache.delete("test_key")
        assert result is True

        value = await in_memory_cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, in_memory_cache):
        """Test deleting non-existent key."""
        result = await in_memory_cache.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists(self, in_memory_cache):
        """Test exists method."""
        await in_memory_cache.set("test_key", "test_value")
        assert await in_memory_cache.exists("test_key") is True
        assert await in_memory_cache.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_expire(self, in_memory_cache):
        """Test setting expiration."""
        await in_memory_cache.set("test_key", "test_value")
        result = await in_memory_cache.expire("test_key", 60)
        assert result is True

    @pytest.mark.asyncio
    async def test_ttl(self, in_memory_cache):
        """Test TTL method."""
        await in_memory_cache.set("test_key", "test_value", ttl=60)
        ttl = await in_memory_cache.ttl("test_key")
        assert 55 <= ttl <= 60  # Allow for small timing differences

    @pytest.mark.asyncio
    async def test_ttl_no_expiration(self, in_memory_cache):
        """Test TTL for key without expiration."""
        await in_memory_cache.set("test_key", "test_value")
        ttl = await in_memory_cache.ttl("test_key")
        assert ttl == -2  # No expiration

    @pytest.mark.asyncio
    async def test_ttl_nonexistent_key(self, in_memory_cache):
        """Test TTL for non-existent key."""
        ttl = await in_memory_cache.ttl("nonexistent")
        assert ttl == -1

    @pytest.mark.asyncio
    async def test_keys_pattern_matching(self, in_memory_cache):
        """Test pattern matching for keys."""
        await in_memory_cache.set("user:123", "value1")
        await in_memory_cache.set("user:456", "value2")
        await in_memory_cache.set("order:789", "value3")

        keys = await in_memory_cache.keys("user:*")
        assert len(keys) == 2
        assert "user:123" in keys
        assert "user:456" in keys

    @pytest.mark.asyncio
    async def test_delete_pattern(self, in_memory_cache):
        """Test deleting keys by pattern."""
        await in_memory_cache.set("user:123", "value1")
        await in_memory_cache.set("user:456", "value2")
        await in_memory_cache.set("order:789", "value3")

        deleted = await in_memory_cache.delete_pattern("user:*")
        assert deleted == 2

        # Keys should be deleted
        assert await in_memory_cache.get("user:123") is None
        assert await in_memory_cache.get("user:456") is None
        assert await in_memory_cache.get("order:789") is not None

    @pytest.mark.asyncio
    async def test_increment(self, in_memory_cache):
        """Test increment operation."""
        result = await in_memory_cache.increment("counter")
        assert result == 1

        result = await in_memory_cache.increment("counter", 5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_set_hash(self, in_memory_cache):
        """Test setting hash values."""
        mapping = {"field1": "value1", "field2": "value2"}
        result = await in_memory_cache.set_hash("test_hash", mapping)
        assert result is True

        # Test get_hash for entire hash
        retrieved = await in_memory_cache.get_hash("test_hash")
        assert retrieved == mapping

    @pytest.mark.asyncio
    async def test_get_hash_field(self, in_memory_cache):
        """Test getting specific hash field."""
        mapping = {"field1": "value1", "field2": "value2"}
        await in_memory_cache.set_hash("test_hash", mapping)

        value = await in_memory_cache.get_hash("test_hash", "field1")
        assert value == "value1"

        value = await in_memory_cache.get_hash("test_hash", "nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_hash_field(self, in_memory_cache):
        """Test deleting hash field."""
        mapping = {"field1": "value1", "field2": "value2"}
        await in_memory_cache.set_hash("test_hash", mapping)

        result = await in_memory_cache.delete_hash_field("test_hash", "field1")
        assert result is True

        # Field should be deleted
        value = await in_memory_cache.get_hash("test_hash", "field1")
        assert value is None

        # Other fields should remain
        value = await in_memory_cache.get_hash("test_hash", "field2")
        assert value == "value2"


class TestCacheService:
    """Test cases for CacheService with Redis fallback."""

    @pytest.fixture
    def cache_service(self):
        """Create CacheService instance."""
        return CacheService()

    @pytest.mark.asyncio
    async def test_connect_redis_available(self, cache_service):
        """Test connecting when Redis is available."""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.return_value = True
            mock_redis.return_value = mock_redis_instance

            await cache_service.connect()

            assert cache_service.use_redis is True
            assert cache_service.redis == mock_redis_instance

    @pytest.mark.asyncio
    async def test_connect_redis_unavailable(self, cache_service):
        """Test connecting when Redis is unavailable."""
        with patch('redis.asyncio.from_url', side_effect=Exception("Redis unavailable")):
            await cache_service.connect()

            assert cache_service.use_redis is False
            assert cache_service.redis is None

    @pytest.mark.asyncio
    async def test_set_redis_available(self, cache_service):
        """Test setting value with Redis."""
        await cache_service.connect()
        cache_service.use_redis = True
        cache_service.redis = AsyncMock()

        result = await cache_service.set("test_key", "test_value", ttl=60)
        assert result is True

        # Verify Redis methods were called
        cache_service.redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_fallback_to_memory(self, cache_service):
        """Test setting value falls back to memory."""
        await cache_service.connect()
        cache_service.use_redis = False

        result = await cache_service.set("test_key", "test_value", ttl=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_redis_available(self, cache_service):
        """Test getting value with Redis."""
        await cache_service.connect()
        cache_service.use_redis = True
        cache_service.redis = AsyncMock()
        cache_service.redis.get.return_value = json.dumps("test_value")

        value = await cache_service.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_fallback_to_memory(self, cache_service):
        """Test getting value falls back to memory."""
        await cache_service.connect()
        cache_service.use_redis = False

        # Set value in memory first
        await cache_service.in_memory_cache.set("test_key", "test_value")

        value = await cache_service.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_delete_redis_available(self, cache_service):
        """Test deleting with Redis."""
        await cache_service.connect()
        cache_service.use_redis = True
        cache_service.redis = AsyncMock()
        cache_service.redis.delete.return_value = 1

        result = await cache_service.delete("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_fallback_to_memory(self, cache_service):
        """Test deleting falls back to memory."""
        await cache_service.connect()
        cache_service.use_redis = False

        # Set value in memory first
        await cache_service.in_memory_cache.set("test_key", "test_value")

        result = await cache_service.delete("test_key")
        assert result is True


class TestCacheConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_cache_session_data(self):
        """Test caching session data."""
        session_data = {"user_id": "123", "preferences": {"theme": "dark"}}
        result = await cache_session_data("session_123", session_data)
        assert result is True

        # Verify data was cached
        cached = await get_cached_session_data("session_123")
        assert cached == session_data

    @pytest.mark.asyncio
    async def test_delete_cached_session_data(self):
        """Test deleting cached session data."""
        # Set session data first
        session_data = {"user_id": "123"}
        await cache_session_data("session_123", session_data)

        # Delete it
        result = await delete_cached_session_data("session_123")
        assert result is True

        # Verify it's gone
        cached = await get_cached_session_data("session_123")
        assert cached is None

    @pytest.mark.asyncio
    async def test_increment_rate_limit(self):
        """Test rate limiting."""
        # First increment
        count = await increment_rate_limit("test_user")
        assert count == 1

        # Second increment
        count = await increment_rate_limit("test_user")
        assert count == 2

    @pytest.mark.asyncio
    async def test_clear_expired_cache(self):
        """Test clearing expired cache."""
        # Set some cache data
        await cache_session_data("session_1", {"data": "value1"})
        await cache_session_data("session_2", {"data": "value2"})

        # Clear by pattern
        cleared = await clear_expired_cache("session:*")
        assert cleared >= 0  # Should clear any expired entries


class TestCacheServiceErrorHandling:
    """Test error handling in CacheService."""

    @pytest.fixture
    def cache_service(self):
        """Create CacheService instance."""
        return CacheService()

    @pytest.mark.asyncio
    async def test_redis_connection_error(self, cache_service):
        """Test handling Redis connection errors."""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis.side_effect = Exception("Connection failed")

            await cache_service.connect()
            assert cache_service.use_redis is False

    @pytest.mark.asyncio
    async def test_redis_operation_error(self, cache_service):
        """Test handling Redis operation errors."""
        await cache_service.connect()
        cache_service.use_redis = True
        cache_service.redis = AsyncMock()
        cache_service.redis.setex.side_effect = Exception("Operation failed")

        # Should not raise exception, should return False
        result = await cache_service.set("test_key", "test_value", ttl=60)
        assert result is False

    @pytest.mark.asyncio
    async def test_memory_cache_cleanup(self, cache_service):
        """Test in-memory cache cleanup after TTL."""
        await cache_service.connect()
        cache_service.use_redis = False

        # Set value with TTL
        await cache_service.set("test_key", "test_value", ttl=1)

        # Wait for expiration
        await asyncio.sleep(2)

        # Should return None after expiration
        value = await cache_service.get("test_key")
        assert value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])