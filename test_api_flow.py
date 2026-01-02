#!/usr/bin/env python3
"""Test session creation and messaging with correct API expectations."""
import asyncio
import httpx
import json

async def test_corrected_conversation():
    """Test creating a session and having a conversation with correct expectations."""
    try:
        async with httpx.AsyncClient() as client:
            # Test creating a session
            session_data = {"visitor_id": "test_visitor_123"}
            response = await client.post("http://localhost:8000/api/v1/sessions", json=session_data)

            print(f"Session creation: {response.status_code}")
            if response.status_code == 201:
                session = response.json()
                session_id = session.get('id')
                print(f"✅ Session created: {session_id}")
                print(f"   Status: {session.get('status')}")
                print(f"   Phase: {session.get('current_phase')}")
                print(f"   Messages: {len(session.get('messages', []))}")

                # Check if we got a welcome message
                messages = session.get('messages', [])
                if messages:
                    welcome_msg = messages[0]
                    print(f"   Bot welcome: {welcome_msg.get('content', 'N/A')[:100]}...")

                # Test sending a name
                print("\n--- Sending user name ---")
                message_data = {"content": "My name is John Doe"}
                headers = {"X-Session-ID": session_id}

                response = await client.post(
                    f"http://localhost:8000/api/v1/sessions/{session_id}/messages",
                    json=message_data,
                    headers=headers
                )

                print(f"Message response: {response.status_code}")
                if response.status_code == 201:
                    user_msg = response.json()
                    print(f"✅ User message sent: {user_msg.get('content', 'N/A')}")
                    print(f"   Message ID: {user_msg.get('id', 'N/A')}")

                    # Check if session was updated
                    session_resp = await client.get(f"http://localhost:8000/api/v1/sessions/{session_id}", headers=headers)
                    if session_resp.status_code == 200:
                        updated_session = session_resp.json()
                        print(f"   Updated client info: {updated_session.get('client_info', {})}")
                        print(f"   Updated phase: {updated_session.get('current_phase')}")
                        print(f"   Total messages: {len(updated_session.get('messages', []))}")

                else:
                    print(f"❌ Error: {response.text}")

                # Test getting session history
                print("\n--- Session history ---")
                session_resp = await client.get(f"http://localhost:8000/api/v1/sessions/{session_id}", headers=headers)
                if session_resp.status_code == 200:
                    session_data = session_resp.json()
                    print(f"✅ Session history retrieved")
                    print(f"   Total messages: {len(session_data.get('messages', []))}")

                    for i, msg in enumerate(session_data.get('messages', [])):
                        role = msg.get('role')
                        content = msg.get('content', '')
                        print(f"   {i+1}. {role}: {content[:80]}...")

            else:
                print(f"❌ Session creation failed: {response.text}")

    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_corrected_conversation())