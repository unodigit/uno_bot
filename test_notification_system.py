#!/usr/bin/env python3
"""
Test notification system (email service)
"""

import requests
import uuid
import json

BASE_URL = "http://localhost:8000"

def test_notification_system():
    print("🧪 Testing Notification System Features")
    print("=" * 50)

    try:
        # Test 1: Create session and complete conversation
        print("1. Creating session and completing conversation...")
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

        # Complete conversation to get qualified
        messages = [
            "Hello",
            "My name is Alice Brown",
            "alice@example.com",
            "I work at TechCorp",
            "We need a custom web application",
            "Technology: React, Python, PostgreSQL",
            "Budget: $40,000",
            "Timeline: 5 months",
            "Success criteria: User-friendly interface"
        ]

        for message in messages:
            requests.post(f"{BASE_URL}/api/v1/sessions/{session_id}/messages", json={"content": message})

        print("   ✅ Conversation completed")

        # Test 2: Get session state
        print("2. Checking session state...")
        session_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
        session_data = session_response.json()

        print(f"   Name: {session_data.get('client_info', {}).get('name', 'N/A')}")
        print(f"   Email: {session_data.get('client_info', {}).get('email', 'N/A')}")
        print(f"   Phase: {session_data.get('current_phase', 'N/A')}")
        print(f"   Lead Score: {session_data.get('lead_score', 'N/A')}")

        # Test 3: Generate PRD
        print("3. Generating PRD...")
        prd_response = requests.post(f"{BASE_URL}/api/v1/prd/generate", json={"session_id": session_id})
        if prd_response.status_code == 200:
            prd_data = prd_response.json()
            print(f"   ✅ PRD Generated: {prd_data.get('id', 'N/A')}")
        else:
            print(f"   ❌ PRD Generation failed: {prd_response.status_code}")

        # Test 4: Check if notification system is configured
        print("4. Checking email service configuration...")
        from src.core.config import settings
        print(f"   SendGrid API Key configured: {'Yes' if settings.sendgrid_api_key else 'No'}")
        print(f"   From Email configured: {'Yes' if settings.sendgrid_from_email else 'No'}")
        print(f"   Environment: {settings.environment}")

        # Test 5: Check if booking flow includes notifications
        print("5. Checking booking endpoints...")
        # Get experts
        experts_response = requests.get(f"{BASE_URL}/api/v1/experts")
        if experts_response.status_code == 200:
            experts = experts_response.json()
            print(f"   ✅ Experts available: {len(experts)}")
            if experts:
                expert = experts[0]
                print(f"   First expert: {expert.get('name', 'N/A')} - {expert.get('role', 'N/A')}")
        else:
            print(f"   ❌ Experts endpoint failed: {experts_response.status_code}")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_notification_system()