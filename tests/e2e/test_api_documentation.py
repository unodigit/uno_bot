"""E2E tests for API documentation (Features #141, #142)

Tests that API documentation is properly generated and accessible:
- Auto-generated API docs at /docs
- OpenAPI spec available at /openapi.json
"""

import requests


class TestAPIDocumentation:
    """Test API documentation features"""

    def test_api_docs_at_slash_docs(self):
        """Verify API documentation is available at /docs

        Feature #141: API documentation is auto-generated at /docs
        """
        print("\n=== Test: API Documentation at /docs ===")

        # Test the backend API directly
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
            print("✅ API docs available at /docs")
        except Exception as e:
            print(f"❌ API docs test failed: {e}")
            raise

    def test_openapi_spec_at_slash_openapi_json(self):
        """Verify OpenAPI spec is available at /openapi.json

        Feature #142: OpenAPI spec available at /openapi.json
        """
        print("\n=== Test: OpenAPI Spec at /openapi.json ===")

        # Test the backend API directly
        try:
            response = requests.get("http://localhost:8000/openapi.json", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify it's valid JSON
            spec = response.json()
            assert "openapi" in spec
            assert "paths" in spec
            assert "info" in spec

            print("✅ OpenAPI spec available at /openapi.json")
            print(f"   Version: {spec.get('openapi', 'N/A')}")
            print(f"   Title: {spec.get('info', {}).get('title', 'N/A')}")
            print(f"   Endpoints: {len(spec.get('paths', {}))}")
        except Exception as e:
            print(f"❌ OpenAPI spec test failed: {e}")
            raise

    def test_api_endpoints_in_spec(self):
        """Verify key endpoints are documented in OpenAPI spec"""
        print("\n=== Test: Key Endpoints Documented ===")

        try:
            response = requests.get("http://localhost:8000/openapi.json", timeout=5)
            spec = response.json()
            paths = spec.get("paths", {})

            # Check for expected endpoints
            expected_endpoints = [
                "/api/v1/sessions",
                "/api/v1/sessions/{session_id}/messages",
                "/api/v1/experts",
            ]

            found_endpoints = []
            for endpoint in expected_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)

            print(f"✅ Found {len(found_endpoints)}/{len(expected_endpoints)} expected endpoints")
            for endpoint in found_endpoints:
                print(f"   - {endpoint}")

            # At least some endpoints should be documented
            assert len(found_endpoints) > 0, "No expected endpoints found in spec"
        except Exception as e:
            print(f"❌ Endpoint documentation test failed: {e}")
            raise

    def test_api_docs_summary(self):
        """Comprehensive summary of API documentation implementation"""
        print("\n=== API Documentation Summary ===")

        results = {
            "docs_at_slash_docs": False,
            "openapi_spec_at_slash_openapi_json": False,
            "key_endpoints_documented": False,
        }

        # Test 1: /docs endpoint
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                results["docs_at_slash_docs"] = True
                print("✅ /docs endpoint: PASS")
            else:
                print(f"❌ /docs endpoint: FAIL (status {response.status_code})")
        except:
            print("❌ /docs endpoint: FAIL (error)")

        # Test 2: /openapi.json endpoint
        try:
            response = requests.get("http://localhost:8000/openapi.json", timeout=5)
            if response.status_code == 200:
                spec = response.json()
                if "openapi" in spec and "paths" in spec:
                    results["openapi_spec_at_slash_openapi_json"] = True
                    print("✅ /openapi.json endpoint: PASS")
                else:
                    print("❌ /openapi.json: Invalid format")
            else:
                print(f"❌ /openapi.json: FAIL (status {response.status_code})")
        except:
            print("❌ /openapi.json endpoint: FAIL (error)")

        # Test 3: Key endpoints documented
        try:
            response = requests.get("http://localhost:8000/openapi.json", timeout=5)
            spec = response.json()
            paths = spec.get("paths", {})
            if any(endpoint in paths for endpoint in ["/api/v1/sessions", "/api/v1/experts"]):
                results["key_endpoints_documented"] = True
                print("✅ Key endpoints documented: PASS")
            else:
                print("❌ Key endpoints documented: FAIL")
        except:
            print("❌ Key endpoints documented: FAIL (error)")

        # Summary
        passed = sum(results.values())
        total = len(results)
        print("\n--- Summary ---")
        print(f"Passed: {passed}/{total}")

        assert passed >= 2, f"API documentation should have at least 2/3 criteria met. Got {passed}/{total}"
        print("✅ API documentation implementation verified")
