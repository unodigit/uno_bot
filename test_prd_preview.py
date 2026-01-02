#!/usr/bin/env python3
"""
Test PRD preview functionality
"""

import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_prd_preview():
    print("🧪 Testing PRD Preview Features")
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
            "My name is Bob Johnson",
            "bob@example.com",
            "I work at MedCorp",
            "We need an appointment scheduling system",
            "Technology: Vue.js, Express, PostgreSQL",
            "Budget: $30,000",
            "Timeline: 4 months",
            "Success criteria: Efficient appointment management"
        ]

        for message in messages:
            requests.post(f"{BASE_URL}/api/v1/sessions/{session_id}/messages", json={"content": message})

        # Generate PRD
        prd_response = requests.post(f"{BASE_URL}/api/v1/prd/generate", json={"session_id": session_id})
        prd_response.raise_for_status()
        prd_data = prd_response.json()
        prd_id = prd_data['id']

        print(f"   ✅ PRD Generated: {prd_id}")

        # Test 2: Test preview endpoint
        print("2. Testing PRD preview...")
        preview_response = requests.get(f"{BASE_URL}/api/v1/prd/{prd_id}/preview")

        print(f"   Preview Status: {preview_response.status_code}")

        if preview_response.status_code == 200:
            preview_data = preview_response.json()
            print(f"   ✅ Preview successful")
            print(f"   PRD ID: {preview_data.get('id', 'N/A')}")
            print(f"   Client: {preview_data.get('client_name', 'N/A')} from {preview_data.get('client_company', 'N/A')}")
            print(f"   Version: {preview_data.get('version', 'N/A')}")

            # Show preview content (first 500 chars)
            content = preview_data.get('content_markdown', '')
            if content:
                print(f"   ✅ Preview content available ({len(content)} characters)")
                print("   Preview:")
                preview_lines = content[:500].split('\n')
                for line in preview_lines[:8]:
                    print(f"     {line}")
                print("     ...")
            else:
                print("   ❌ No preview content")

            return True
        else:
            print(f"   ❌ Preview failed: {preview_response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_prd_preview()