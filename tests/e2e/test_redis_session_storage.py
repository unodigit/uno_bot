"""E2E tests for Redis session storage (Feature #148)

Tests that session data is properly stored and retrieved from Redis:
- Session creation stores data in Redis
- Session data persists with correct TTL (7 days)
- Session data can be retrieved from Redis
- Session data matches database content
"""

import json

import pytest
import redis
import requests


class TestRedisSessionStorage:
    """Test Redis session storage functionality"""

    def test_session_data_stored_in_redis(self):
        """Verify session data is stored in Redis when session is created

        Feature #148: Session data stored in Redis correctly
        """
        print("\n=== Test: Session Data Stored in Redis ===")

        # Create a new session
        session_data = {
            "visitor_id": "test_visitor_redis_001",
            "source_url": "http://localhost:5173/test",
            "user_agent": "Test Agent"
        }

        response = requests.post(
            "http://localhost:8000/api/v1/sessions",
            json=session_data,
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        session_response = response.json()
        session_id = session_response["id"]

        print(f"Created session: {session_id}")

        # Try to connect to Redis and check if session key exists
        try:
            redis_client = redis.Redis.from_url("redis://localhost:6379", socket_connect_timeout=2)
            redis_status = "healthy"
        except redis.ConnectionError:
            redis_status = "unavailable"
            print("⚠️ Redis not available - skipping Redis storage verification")
            pytest.skip("Redis not available")

        if redis_status == "healthy":
            # Check if session key exists in Redis
            redis_key = f"session:{session_id}"
            session_data_redis = redis_client.get(redis_key)

            if session_data_redis:
                session_json = json.loads(session_data_redis)
                print(f"✅ Session found in Redis: {redis_key}")
                print(f"   Data: {session_json}")
            else:
                print(f"❌ Session not found in Redis: {redis_key}")
                pytest.fail("Session data should be stored in Redis")

    def test_session_data_ttl_matches_7_days(self):
        """Verify session data TTL is set to 7 days

        Feature #148: Session data stored in Redis correctly
        """
        print("\n=== Test: Session Data TTL Matches 7 Days ===")

        # Create a new session
        session_data = {
            "visitor_id": "test_visitor_redis_ttl_001",
            "source_url": "http://localhost:5173/test",
            "user_agent": "Test Agent"
        }

        response = requests.post(
            "http://localhost:8000/api/v1/sessions",
            json=session_data,
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        session_response = response.json()
        session_id = session_response["id"]

        try:
            redis_client = redis.Redis.from_url("redis://localhost:6379", socket_connect_timeout=2)
        except redis.ConnectionError:
            print("⚠️ Redis not available - skipping TTL verification")
            pytest.skip("Redis not available")

        # Check TTL of session key
        redis_key = f"session:{session_id}"
        ttl = redis_client.ttl(redis_key)

        if ttl > 0:
            # TTL should be approximately 7 days (604800 seconds)
            expected_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
            tolerance = 60  # 1 minute tolerance

            print(f"   TTL: {ttl} seconds")
            print(f"   Expected: ~{expected_ttl} seconds")

            # Allow some tolerance for Redis precision
            if abs(ttl - expected_ttl) <= tolerance:
                print(f"✅ TTL matches 7 days: {ttl} seconds")
            else:
                print(f"❌ TTL doesn't match 7 days: {ttl} vs {expected_ttl}")
                pytest.fail(f"TTL should be approximately {expected_ttl} seconds, got {ttl}")
        else:
            print(f"❌ No TTL set for session key: {redis_key}")
            pytest.fail("Session key should have TTL set")

    def test_session_data_retrieved_from_redis(self):
        """Verify session data can be retrieved from Redis

        Feature #148: Session data stored in Redis correctly
        """
        print("\n=== Test: Session Data Retrieved from Redis ===")

        # Create a new session
        session_data = {
            "visitor_id": "test_visitor_redis_retrieve_001",
            "source_url": "http://localhost:5173/test",
            "user_agent": "Test Agent"
        }

        response = requests.post(
            "http://localhost:8000/api/v1/sessions",
            json=session_data,
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        session_response = response.json()
        session_id = session_response["id"]

        try:
            redis_client = redis.Redis.from_url("redis://localhost:6379", socket_connect_timeout=2)
        except redis.ConnectionError:
            print("⚠️ Redis not available - skipping retrieval verification")
            pytest.skip("Redis not available")

        # Retrieve session data from Redis
        redis_key = f"session:{session_id}"
        session_data_redis = redis_client.get(redis_key)

        if session_data_redis:
            session_json = json.loads(session_data_redis)
            print(f"✅ Session data retrieved from Redis: {redis_key}")
            print(f"   Visitor ID: {session_json.get('visitor_id')}")
            print(f"   Source URL: {session_json.get('source_url')}")
            print(f"   User Agent: {session_json.get('user_agent')}")
        else:
            print(f"❌ Session data not found in Redis: {redis_key}")
            pytest.fail("Session data should be retrievable from Redis")

    def test_session_data_matches_database(self):
        """Verify session data in Redis matches database content

        Feature #148: Session data stored in Redis correctly
        """
        print("\n=== Test: Session Data Matches Database ===")

        # Create a new session
        session_data = {
            "visitor_id": "test_visitor_redis_match_001",
            "source_url": "http://localhost:5173/test",
            "user_agent": "Test Agent"
        }

        response = requests.post(
            "http://localhost:8000/api/v1/sessions",
            json=session_data,
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        session_response = response.json()
        session_id = session_response["id"]

        try:
            redis_client = redis.Redis.from_url("redis://localhost:6379", socket_connect_timeout=2)
        except redis.ConnectionError:
            print("⚠️ Redis not available - skipping match verification")
            pytest.skip("Redis not available")

        # Get session from API (which reads from database)
        api_response = requests.get(
            f"http://localhost:8000/api/v1/sessions/{session_id}",
            timeout=10
        )
        assert api_response.status_code == 200, f"Expected 200, got {api_response.status_code}"

        session_from_api = api_response.json()

        # Get session from Redis
        redis_key = f"session:{session_id}"
        session_data_redis = redis_client.get(redis_key)

        if session_data_redis:
            session_from_redis = json.loads(session_data_redis)

            # Compare key fields
            api_visitor_id = session_from_api.get("visitor_id")
            redis_visitor_id = session_from_redis.get("visitor_id")

            api_source_url = session_from_api.get("source_url")
            redis_source_url = session_from_redis.get("source_url")

            api_user_agent = session_from_api.get("user_agent")
            redis_user_agent = session_from_redis.get("user_agent")

            print(f"   API Visitor ID: {api_visitor_id}")
            print(f"   Redis Visitor ID: {redis_visitor_id}")
            print(f"   API Source URL: {api_source_url}")
            print(f"   Redis Source URL: {redis_source_url}")
            print(f"   API User Agent: {api_user_agent}")
            print(f"   Redis User Agent: {redis_user_agent}")

            # Verify they match
            assert api_visitor_id == redis_visitor_id, "Visitor IDs don't match"
            assert api_source_url == redis_source_url, "Source URLs don't match"
            assert api_user_agent == redis_user_agent, "User agents don't match"

            print("✅ Session data matches between API and Redis")
        else:
            print(f"❌ Session data not found in Redis: {redis_key}")
            pytest.fail("Session data should be retrievable from Redis")

    def test_redis_session_storage_summary(self):
        """Comprehensive summary of Redis session storage implementation

        Feature #148: Session data stored in Redis correctly
        """
        print("\n=== Redis Session Storage Summary ===")

        # Check Redis availability
        try:
            redis_client = redis.Redis.from_url("redis://localhost:6379", socket_connect_timeout=2)
            redis_available = True
            print("✅ Redis is available")
        except redis.ConnectionError:
            redis_available = False
            print("⚠️ Redis is not available")

        if not redis_available:
            print("❌ Redis session storage cannot be verified without Redis server")
            pytest.fail("Redis server required for session storage verification")

        # Test basic Redis functionality
        try:
            redis_client.set("test_key", "test_value", ex=60)
            test_value = redis_client.get("test_key")
            redis_client.delete("test_key")

            if test_value == b"test_value":
                print("✅ Redis read/write operations working")
            else:
                print("❌ Redis read/write operations failed")
                pytest.fail("Redis operations not working")

        except Exception as e:
            print(f"❌ Redis operations failed: {e}")
            pytest.fail(f"Redis operations failed: {e}")

        # The actual session storage implementation would need to be added
        # to the session service to store session data in Redis
        print("\n📝 Note: Current implementation uses in-memory session storage")
        print("📝 Session data is not automatically stored in Redis")
        print("📝 Redis session storage implementation would need to be added")
        print("📝 to the SessionService.create_session() and related methods")

        print("\n--- Summary ---")
        print("❌ Redis session storage not currently implemented")
        print("📝 Backend has Redis configuration but no session storage logic")
        print("📝 WebSocket manager uses in-memory storage only")
        print("📝 Feature requires Redis session storage implementation")
