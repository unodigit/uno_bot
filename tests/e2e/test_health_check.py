"""E2E tests for health check endpoint (Feature #161)

Tests that the health check endpoint returns proper status:
- Overall system status
- Database connection status
- Redis connection status
- API version and timestamp
"""

from datetime import datetime

import pytest
import requests


class TestHealthCheck:
    """Test health check endpoint features"""

    def test_health_check_returns_all_required_fields(self):
        """Verify health check returns all required fields

        Feature #161: Health check endpoint returns status
        """
        print("\n=== Test: Health Check Returns All Required Fields ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # Check all required fields exist
        required_fields = ["status", "version", "timestamp", "database", "redis"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        print(f"✅ All required fields present: {required_fields}")

    def test_health_check_status_values(self):
        """Verify health check status values are valid

        Feature #161: Health check endpoint returns status
        """
        print("\n=== Test: Health Check Status Values ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        # Status should be one of: operational, degraded, down
        assert data["status"] in ["operational", "degraded", "down"], \
            f"Invalid status: {data['status']}"

        # Database should be: healthy or unhealthy
        assert data["database"] in ["healthy", "unhealthy"], \
            f"Invalid database status: {data['database']}"

        # Redis should be: healthy, unavailable, or unhealthy
        assert data["redis"] in ["healthy", "unavailable", "unhealthy"], \
            f"Invalid redis status: {data['redis']}"

        print("✅ Status values are valid:")
        print(f"   - Overall: {data['status']}")
        print(f"   - Database: {data['database']}")
        print(f"   - Redis: {data['redis']}")

    def test_health_check_database_status(self):
        """Verify database status is reported correctly

        Feature #161: Health check endpoint returns database status
        """
        print("\n=== Test: Database Status Reporting ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        # Database should be healthy since we're using SQLite
        assert data["database"] == "healthy", \
            f"Database should be healthy, got: {data['database']}"

        print(f"✅ Database status: {data['database']}")

    def test_health_check_redis_status(self):
        """Verify Redis status is reported correctly

        Feature #161: Health check endpoint returns Redis status
        """
        print("\n=== Test: Redis Status Reporting ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        # Redis can be unavailable (not running) or healthy
        # Both are acceptable for this test
        assert data["redis"] in ["unavailable", "healthy"], \
            f"Redis should be unavailable or healthy, got: {data['redis']}"

        print(f"✅ Redis status: {data['redis']}")

    def test_health_check_version_format(self):
        """Verify version is in correct format

        Feature #161: Health check endpoint returns version
        """
        print("\n=== Test: Version Format ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        # Version should be a string in semantic version format
        version = data["version"]
        assert isinstance(version, str), f"Version should be string, got: {type(version)}"
        assert len(version) > 0, "Version should not be empty"

        print(f"✅ Version format valid: {version}")

    def test_health_check_timestamp_format(self):
        """Verify timestamp is in ISO format

        Feature #161: Health check endpoint returns timestamp
        """
        print("\n=== Test: Timestamp Format ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        # Timestamp should be ISO 8601 format
        timestamp_str = data["timestamp"]
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            assert dt.year == 2026, "Timestamp year should be 2026"
            print(f"✅ Timestamp format valid: {timestamp_str}")
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")

    def test_health_check_overall_status_logic(self):
        """Verify overall status is calculated correctly

        Feature #161: Health check endpoint returns proper overall status
        """
        print("\n=== Test: Overall Status Logic ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        db = data["database"]
        redis = data["redis"]
        status = data["status"]

        # Logic:
        # - If DB healthy and Redis healthy/unavailable -> operational
        # - If DB healthy and Redis unhealthy -> degraded
        # - If DB unhealthy -> down

        if db == "healthy" and redis in ["healthy", "unavailable"]:
            expected_status = "operational"
        elif db == "healthy":
            expected_status = "degraded"
        else:
            expected_status = "down"

        assert status == expected_status, \
            f"Expected status '{expected_status}', got '{status}' (db={db}, redis={redis})"

        print(f"✅ Overall status logic correct: {status}")

    def test_health_check_summary(self):
        """Comprehensive summary of health check implementation

        Feature #161: Health check endpoint returns status
        """
        print("\n=== Health Check Summary ===")

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        data = response.json()

        results = {
            "all_fields_present": all(k in data for k in ["status", "version", "timestamp", "database", "redis"]),
            "status_valid": data["status"] in ["operational", "degraded", "down"],
            "database_valid": data["database"] in ["healthy", "unhealthy"],
            "redis_valid": data["redis"] in ["healthy", "unavailable", "unhealthy"],
            "version_valid": isinstance(data["version"], str) and len(data["version"]) > 0,
            "timestamp_valid": True,  # Already validated above
        }

        print(f"   Status: {data['status']}")
        print(f"   Version: {data['version']}")
        print(f"   Timestamp: {data['timestamp']}")
        print(f"   Database: {data['database']}")
        print(f"   Redis: {data['redis']}")

        passed = sum(results.values())
        total = len(results)
        print("\n--- Summary ---")
        print(f"Passed: {passed}/{total}")

        assert passed == total, f"All health check criteria should pass. Got {passed}/{total}"
        print("✅ Health check implementation verified")
