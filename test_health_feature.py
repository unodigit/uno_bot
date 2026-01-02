"""Test Feature 161: Health check endpoint returns status."""
import asyncio
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import time

# Test using direct HTTP requests
import urllib.request
import urllib.error


def test_health_endpoint():
    """Test that the health check endpoint returns proper status."""
    print("=" * 70)
    print("Testing Feature 161: Health Check Endpoint")
    print("=" * 70)

    base_url = "http://localhost:8000"

    # Test 1: GET /api/v1/health
    print("\n[Test 1] GET /api/v1/health")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/v1/health", timeout=5)
        status_code = response.status
        data = json.loads(response.read().decode())

        print(f"  Status Code: {status_code}")
        print(f"  Response: {json.dumps(data, indent=4)}")

        # Verify 200 response
        assert status_code == 200, f"Expected 200, got {status_code}"
        print("  ✓ 200 OK response verified")

        # Verify status field exists
        assert "status" in data, "Response missing 'status' field"
        print(f"  ✓ Status field present: {data['status']}")

        # Verify database status
        assert "database" in data or "checks" in data, "Response missing database status"
        if "database" in data:
            print(f"  ✓ Database status present: {data['database']}")
        elif "checks" in data and "database" in data["checks"]:
            print(f"  ✓ Database check present: {data['checks']['database']}")

        # Verify timestamp
        assert "timestamp" in data, "Response missing 'timestamp' field"
        print(f"  ✓ Timestamp present: {data['timestamp']}")

        # Verify version
        assert "version" in data, "Response missing 'version' field"
        print(f"  ✓ Version present: {data['version']}")

        print("\n✅ Test 1 PASSED: Health endpoint returns all required fields")
        return True

    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP Error: {e.code} - {e.reason}")
        print(f"  Response: {e.read().decode()}")
        return False
    except urllib.error.URLError as e:
        print(f"  ✗ Connection Error: {e.reason}")
        print("  Hint: Make sure backend server is running on port 8000")
        return False
    except AssertionError as e:
        print(f"  ✗ Assertion Failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alternative_health_paths():
    """Test alternative health check paths."""
    print("\n" + "=" * 70)
    print("Testing Alternative Health Paths")
    print("=" * 70)

    base_url = "http://localhost:8000"
    paths = [
        "/health",
        "/api/health",
        "/api/v1/health/detailed",
    ]

    results = []
    for path in paths:
        print(f"\n[Test] GET {path}")
        try:
            response = urllib.request.urlopen(f"{base_url}{path}", timeout=5)
            status_code = response.status
            data = json.loads(response.read().decode())
            print(f"  ✓ Status: {status_code}")
            print(f"  ✓ Response: {json.dumps(data, indent=2)[:200]}...")
            results.append((path, True, None))
        except urllib.error.HTTPError as e:
            print(f"  ✗ HTTP Error: {e.code}")
            results.append((path, False, f"HTTP {e.code}"))
        except urllib.error.URLError as e:
            print(f"  ✗ Not Found (expected for some paths)")
            results.append((path, False, "Not Found"))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((path, False, str(e)))

    print(f"\n{'Path':<30} {'Status':<10} {'Error'}")
    print("-" * 70)
    for path, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        error = error or "-"
        print(f"{path:<30} {status:<10} {error}")

    return any(success for _, success, _ in results)


def test_health_response_format():
    """Test the health response format matches specification."""
    print("\n" + "=" * 70)
    print("Testing Health Response Format")
    print("=" * 70)

    try:
        response = urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=5)
        data = json.loads(response.read().decode())

        print("\nExpected fields check:")
        expected_fields = {
            "status": str,
            "version": str,
            "timestamp": str,
        }

        all_present = True
        for field, field_type in expected_fields.items():
            if field in data:
                actual_type = type(data[field]).__name__
                expected_type_name = field_type.__name__
                match = isinstance(data[field], field_type)
                status = "✓" if match else "✗"
                print(f"  {status} {field}: {actual_type} (expected {expected_type_name})")
                if not match:
                    all_present = False
            else:
                print(f"  ✗ {field}: MISSING")
                all_present = False

        # Check optional database/redis fields
        print("\nOptional fields check:")
        optional_fields = ["database", "redis"]
        for field in optional_fields:
            if field in data:
                print(f"  ✓ {field}: {data[field]}")
            else:
                print(f"  ℹ {field}: Not present (optional)")

        if all_present:
            print("\n✅ Response format validation PASSED")
            return True
        else:
            print("\n✗ Response format validation FAILED")
            return False

    except Exception as e:
        print(f"\n✗ Error testing response format: {e}")
        return False


def main():
    """Run all health check tests."""
    print("\n" + "=" * 70)
    print("FEATURE 161: HEALTH CHECK ENDPOINT TEST SUITE")
    print("=" * 70)

    results = []

    # Test 1: Basic health check
    result1 = test_health_endpoint()
    results.append(("Basic Health Check", result1))

    # Test 2: Alternative paths
    result2 = test_alternative_health_paths()
    results.append(("Alternative Paths", result2))

    # Test 3: Response format
    result3 = test_health_response_format()
    results.append(("Response Format", result3))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "✗ FAIL"
        print(f"{status:<10} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Feature 161 is complete!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
