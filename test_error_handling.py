#!/usr/bin/env python3
"""Test script to verify API error handling."""

import asyncio
import httpx
import json

async def test_error_handling():
    """Test various error scenarios."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("Testing API Error Handling...")
        print("=" * 50)

        # Test 1: Invalid session ID (404)
        print("\n1. Testing invalid session ID...")
        try:
            response = await client.get(f"{base_url}/api/v1/sessions/00000000-0000-0000-0000-000000000000")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        # Test 4: Valid UUID but non-existent session
        print("\n4. Testing non-existent session with valid UUID...")
        try:
            response = await client.get(f"{base_url}/api/v1/sessions/12345678-1234-1234-1234-123456789012")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        # Test 2: Invalid JSON data (422)
        print("\n2. Testing invalid JSON data...")
        try:
            response = await client.post(
                f"{base_url}/api/v1/sessions",
                json={"invalid_field": "test"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        # Test 3: Missing required field (422)
        print("\n3. Testing missing required field...")
        try:
            response = await client.post(
                f"{base_url}/api/v1/sessions",
                json={}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "=" * 50)
        print("Error handling test completed!")

if __name__ == "__main__":
    asyncio.run(test_error_handling())