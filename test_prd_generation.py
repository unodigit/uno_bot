#!/usr/bin/env python3
"""
Test PRD generation functionality
"""

import asyncio
import json
import requests
import uuid
import time

BASE_URL = "http://localhost:8000"

def test_prd_generation():
    print("🧪 Testing PRD Generation Features")
    print("=" * 50)

    try:
        # Test 1: Create session and complete conversation
        print("1. Creating session and simulating conversation...")
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

        # Simulate a complete conversation to trigger PRD generation
        conversation = [
            "Hello",  # Greeting
            "My name is John Doe",  # Provide name
            "john@example.com",  # Provide email
            "I work at Acme Corp",  # Provide company
            "We need a healthcare management system",  # Business challenge
            "Technology: React, Node.js",  # Tech stack
            "Budget: $50,000",  # Budget
            "Timeline: 6 months",  # Timeline
            "Success criteria: Improve patient management",  # Success criteria
            "Generate PRD"  # Request PRD generation
        ]

        print("2. Simulating conversation...")
        for i, message in enumerate(conversation):
            print(f"   Message {i+1}: {message}")
            response = requests.post(
                f"{BASE_URL}/api/v1/sessions/{session_id}/messages",
                json={"content": message}
            )
            response.raise_for_status()
            time.sleep(0.5)  # Small delay between messages

        print("   ✅ Conversation completed")

        # Test 2: Check session state
        print("3. Checking session state...")
        session_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
        session_data = session_response.json()

        client_info = session_data.get('client_info', {})
        business_context = session_data.get('business_context', {})
        qualification = session_data.get('qualification', {})

        print(f"   Name: {client_info.get('name', 'N/A')}")
        print(f"   Email: {client_info.get('email', 'N/A')}")
        print(f"   Company: {business_context.get('company', 'N/A')}")
        print(f"   Lead Score: {session_data.get('lead_score', 'N/A')}")
        print(f"   Recommended Service: {session_data.get('recommended_service', 'N/A')}")
        print(f"   Current Phase: {session_data.get('current_phase', 'N/A')}")
        print(f"   PRD ID: {session_data.get('prd_id', 'N/A')}")

        # Test 3: Try to generate PRD
        print("4. Attempting PRD generation...")
        prd_response = requests.post(
            f"{BASE_URL}/api/v1/prd/generate",
            json={"session_id": session_id}
        )

        if prd_response.status_code == 200:
            prd_data = prd_response.json()
            print(f"   ✅ PRD Generated: {prd_data.get('id', 'N/A')}")
            print(f"   PRD URL: {prd_data.get('storage_url', 'N/A')}")
            return True
        else:
            print(f"   ❌ PRD Generation failed: {prd_response.status_code}")
            print(f"   Response: {prd_response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_prd_generation()