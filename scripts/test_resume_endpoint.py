#!/usr/bin/env python3
"""Test script for resume endpoint."""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx


async def test_resume_endpoint():
    """Test the resume session endpoint."""
    base_url = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        # Step 1: Create a new session
        print("=" * 60)
        print("Step 1: Creating new session")
        print("=" * 60)

        response = await client.post(f"{base_url}/api/v1/sessions", json={
            "visitor_id": "test_resume_visitor",
            "source_url": "http://localhost:5173",
            "user_agent": "Test/1.0"
        })

        print(f"Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error: {response.text}")
            return False

        session = response.json()
        session_id = session["id"]
        print(f"Session ID: {session_id}")
        print(f"Messages: {len(session['messages'])}")
        print(f"Status: {session['status']}")

        # Step 2: Test resume with path-based endpoint
        print("\n" + "=" * 60)
        print("Step 2: Testing POST /api/v1/sessions/{id}/resume")
        print("=" * 60)

        response = await client.post(f"{base_url}/api/v1/sessions/{session_id}/resume")
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        resumed = response.json()
        print(f"Resumed Session ID: {resumed['id']}")
        print(f"Messages after resume: {len(resumed['messages'])}")
        print(f"Status: {resumed['status']}")

        # Step 3: Test resume with body-based endpoint
        print("\n" + "=" * 60)
        print("Step 3: Testing POST /api/v1/sessions/resume")
        print("=" * 60)

        response = await client.post(f"{base_url}/api/v1/sessions/resume", json={
            "session_id": str(session_id)
        })
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        resumed2 = response.json()
        print(f"Resumed Session ID: {resumed2['id']}")
        print(f"Messages after resume: {len(resumed2['messages'])}")
        print(f"Status: {resumed2['status']}")

        # Step 4: Verify both methods return same data
        print("\n" + "=" * 60)
        print("Step 4: Verifying consistency")
        print("=" * 60)

        if resumed["id"] == resumed2["id"] and len(resumed["messages"]) == len(resumed2["messages"]):
            print("✓ Both resume methods return consistent data")
            return True
        else:
            print("✗ Resume methods return inconsistent data")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_resume_endpoint())
    sys.exit(0 if success else 1)
