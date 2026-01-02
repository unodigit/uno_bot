#!/usr/bin/env python3
"""
Test to verify AI messages are being created in the database
"""

import asyncio
import json
import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_database_messages():
    print("🔍 Testing if AI messages are created in database...")

    try:
        # Test 1: Create session
        print("1. Creating new session...")
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

        # Test 2: Send message and check messages
        print("2. Sending message and checking all messages...")
        message_response = requests.post(
            f"{BASE_URL}/api/v1/sessions/{session_id}/messages",
            json={"content": "Hello"}
        )
        print(f"   Message HTTP response: {message_response.status_code}")
        print(f"   Message returned: {message_response.json()}")

        # Test 3: Get session and check all messages
        print("3. Getting session to check all messages...")
        session_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
        session_data = session_response.json()

        messages = session_data.get('messages', [])
        print(f"   Total messages in session: {len(messages)}")

        for i, msg in enumerate(messages):
            print(f"   Message {i+1}: {msg['role']} - '{msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}'")

        # Check if we have an AI response
        ai_messages = [msg for msg in messages if msg['role'] == 'assistant']
        if ai_messages:
            print(f"   ✅ AI message found: '{ai_messages[0]['content'][:100]}...'")
            return True
        else:
            print("   ❌ No AI message found")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_database_messages()