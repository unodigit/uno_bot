#!/usr/bin/env python3
"""Test session creation and basic functionality."""
import asyncio
import httpx
import json

async def test_session_creation():
    """Test creating a new chat session."""
    try:
        async with httpx.AsyncClient() as client:
            # Test creating a session
            session_data = {"visitor_id": "test_visitor_123"}
            response = await client.post("http://localhost:8000/api/v1/sessions", json=session_data)

            print(f"Session creation: {response.status_code}")
            if response.status_code == 200:
                session = response.json()
                print(f"Session ID: {session.get('id')}")
                print(f"Session status: {session.get('status')}")
                print(f"Messages: {len(session.get('messages', []))}")
            else:
                print(f"Error: {response.text}")

            # Test sending a message
            if response.status_code == 200:
                session_id = session.get('id')
                message_data = {"content": "Hello, I need help with a business project"}
                headers = {"X-Session-ID": session_id}

                response = await client.post(
                    f"http://localhost:8000/api/v1/sessions/{session_id}/messages",
                    json=message_data,
                    headers=headers
                )

                print(f"Message sending: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"User message: {result.get('user_message', {}).get('content', 'N/A')}")
                    print(f"AI response: {result.get('ai_message', {}).get('content', 'N/A')[:100]}...")
                else:
                    print(f"Error: {response.text}")

    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_session_creation())