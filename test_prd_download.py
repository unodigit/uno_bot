#!/usr/bin/env python3
"""
Test PRD download functionality
"""

import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_prd_download():
    print("🧪 Testing PRD Download Features")
    print("=" * 50)

    try:
        # Test 1: Create session and generate PRD
        print("1. Creating session and generating PRD...")
        session_data = {
            "visitor_id": str(uuid.uuid4()),
            "source_url": "http://localhost:5173/test",
            "user_agent": "Test Script"
        }

        response = requests.post(f"{BASE_URL}/api/v1/sessions", json=session_data)
        response.raise_for_status()
        session_response = response.json()
        session_id = session_response['id']
        print(f"   ✅ Session created: {session_id}")

        # Simulate conversation
        messages = [
            "Hello",
            "My name is Jane Smith",
            "jane@example.com",
            "I work at HealthTech Inc",
            "We need a patient management system",
            "Technology: React, Node.js, MongoDB",
            "Budget: $75,000",
            "Timeline: 8 months",
            "Success criteria: Better patient tracking"
        ]

        for message in messages:
            requests.post(f"{BASE_URL}/api/v1/sessions/{session_id}/messages", json={"content": message})

        # Generate PRD
        prd_response = requests.post(f"{BASE_URL}/api/v1/prd/generate", json={"session_id": session_id})
        prd_response.raise_for_status()
        prd_data = prd_response.json()
        prd_id = prd_data['id']
        download_url = prd_data['storage_url']

        print(f"   ✅ PRD Generated: {prd_id}")
        print(f"   Download URL: {download_url}")

        # Test 2: Test download endpoint
        print("2. Testing PRD download...")
        download_response = requests.get(f"{BASE_URL}{download_url}")

        print(f"   Download Status: {download_response.status_code}")
        print(f"   Content-Type: {download_response.headers.get('content-type', 'N/A')}")
        print(f"   Content-Disposition: {download_response.headers.get('content-disposition', 'N/A')}")

        if download_response.status_code == 200:
            content = download_response.text
            print(f"   ✅ Download successful")
            print(f"   Content Length: {len(content)} characters")

            # Check if it's valid markdown
            if "# Project Requirements Document" in content:
                print("   ✅ Valid PRD content detected")
            else:
                print("   ❌ Invalid PRD content")

            # Show first few lines
            lines = content.split('\n')[:10]
            print("   Preview:")
            for line in lines:
                print(f"     {line}")

            return True
        else:
            print(f"   ❌ Download failed: {download_response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_prd_download()