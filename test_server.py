#!/usr/bin/env python3
"""Simple server test script."""
import asyncio
import httpx

async def test_server():
    try:
        async with httpx.AsyncClient() as client:
            # Test root endpoint
            response = await client.get("http://localhost:8000/")
            print(f"Root endpoint: {response.status_code}")
            print(f"Response: {response.json()}")

            # Test docs endpoint
            response = await client.get("http://localhost:8000/docs")
            print(f"Docs endpoint: {response.status_code}")

            # Test health endpoint
            response = await client.get("http://localhost:8000/api/v1/health")
            print(f"Health endpoint: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())