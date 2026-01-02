#!/usr/bin/env python3
"""Test script for PRD generation."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx


async def test_prd_generation():
    """Test the PRD generation flow."""
    base_url = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        # Step 1: Create a new session
        print("=" * 60)
        print("Step 1: Creating new session")
        print("=" * 60)

        response = await client.post(f"{base_url}/api/v1/sessions", json={
            "visitor_id": "test_prd_visitor",
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
        print(f"Status: {session['status']}")
        print(f"Phase: {session['current_phase']}")

        # Step 2: Simulate a full qualification conversation
        print("\n" + "=" * 60)
        print("Step 2: Simulating qualification conversation")
        print("=" * 60)

        messages = [
            "My name is John Smith",
            "My email is john@example.com",
            "I work at TechCorp Inc",
            "We're in the healthcare industry",
            "We need help with AI and data analytics",
            "Our current stack is Python and PostgreSQL",
            "Budget is around $75,000",
            "We need this completed within 3 months"
        ]

        for msg in messages:
            response = await client.post(
                f"{base_url}/api/v1/sessions/{session_id}/messages",
                json={"content": msg}
            )
            print(f"Sent: {msg}")
            if response.status_code != 201:
                print(f"  Error: {response.text}")
                return False

        # Step 3: Check session data
        print("\n" + "=" * 60)
        print("Step 3: Checking collected session data")
        print("=" * 60)

        response = await client.get(f"{base_url}/api/v1/sessions/{session_id}")
        session = response.json()

        print(f"Client Info: {session.get('client_info', {})}")
        print(f"Business Context: {session.get('business_context', {})}")
        print(f"Qualification: {session.get('qualification', {})}")
        print(f"Lead Score: {session.get('lead_score')}")
        print(f"Recommended Service: {session.get('recommended_service')}")

        # Step 4: Generate PRD
        print("\n" + "=" * 60)
        print("Step 4: Generating PRD")
        print("=" * 60)

        response = await client.post(
            f"{base_url}/api/v1/prd/generate?session_id={session_id}"
        )
        print(f"Status: {response.status_code}")

        if response.status_code != 201:
            print(f"Error: {response.text}")
            return False

        prd = response.json()
        print(f"PRD ID: {prd['id']}")
        print(f"Version: {prd['version']}")
        print(f"Client: {prd['client_name']} from {prd['client_company']}")

        # Step 5: Check PRD content
        print("\n" + "=" * 60)
        print("Step 5: Validating PRD content")
        print("=" * 60)

        content = prd['content_markdown']

        required_sections = [
            "Executive Summary",
            "Business Objectives",
            "Technical Requirements",
            "Scope",
            "Timeline",
            "Success Criteria"
        ]

        missing_sections = []
        for section in required_sections:
            if section in content:
                print(f"✓ Found: {section}")
            else:
                print(f"✗ Missing: {section}")
                missing_sections.append(section)

        if missing_sections:
            print(f"\n⚠ PRD is missing sections: {missing_sections}")
            print(f"\nFirst 500 characters of PRD:\n{content[:500]}...")
            return False

        # Step 6: Test PRD preview
        print("\n" + "=" * 60)
        print("Step 6: Testing PRD preview")
        print("=" * 60)

        response = await client.get(f"{base_url}/api/v1/prd/{prd['id']}/preview")
        print(f"Preview status: {response.status_code}")

        if response.status_code == 200:
            preview = response.json()
            print(f"Filename: {preview['filename']}")
            print(f"Preview text: {preview['preview_text'][:100]}...")
        else:
            print(f"Error: {response.text}")
            return False

        # Step 7: Test PRD download
        print("\n" + "=" * 60)
        print("Step 7: Testing PRD download")
        print("=" * 60)

        response = await client.get(f"{base_url}/api/v1/prd/{prd['id']}/download")
        print(f"Download status: {response.status_code}")

        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Disposition: {response.headers.get('content-disposition')}")
            print(f"Content length: {len(response.content)} bytes")
        else:
            print(f"Error: {response.text}")
            return False

        print("\n" + "=" * 60)
        print("✓ All PRD tests passed!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_prd_generation())
    sys.exit(0 if success else 1)
