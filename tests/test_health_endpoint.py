"""Test health check endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_status():
    """Test that GET /api/v1/health returns application health status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["operational", "degraded", "down"]
        assert "version" in data
        assert "timestamp" in data
        assert "database" in data
        assert data["database"] in ["healthy", "unavailable", "error"]


@pytest.mark.asyncio
async def test_health_endpoint_includes_database_status():
    """Test that health check includes database connectivity status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        # Database status should be present
        assert "database" in data
        assert isinstance(data["database"], str)


@pytest.mark.asyncio
async def test_health_endpoint_returns_version():
    """Test that health check returns application version."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


@pytest.mark.asyncio
async def test_health_endpoint_includes_timestamp():
    """Test that health check includes current timestamp."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)


@pytest.mark.asyncio
async def test_detailed_health_endpoint():
    """Test that GET /api/v1/admin/health/detailed returns comprehensive health info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/health/detailed")

        assert response.status_code == 200
        data = response.json()

        # Should have success flag
        assert "success" in data
        assert data["success"] is True

        # Should have data with checks
        assert "data" in data
        assert "checks" in data["data"]
        assert isinstance(data["data"]["checks"], dict)


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        """Run health endpoint tests."""
        print("Testing health check endpoint...")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test basic health endpoint
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            print(f"✓ Health endpoint status: {response.status_code}")
            print(f"✓ Response: {data}")

            # Verify required fields
            assert "status" in data
            assert "version" in data
            assert "timestamp" in data
            assert "database" in data
            print("✓ All required fields present")

            # Test detailed health endpoint
            response = await client.get("/api/v1/health/detailed")
            assert response.status_code == 200
            data = response.json()
            print(f"✓ Detailed health endpoint status: {response.status_code}")

        print("\n✅ All health endpoint tests passed!")

    asyncio.run(run_tests())
