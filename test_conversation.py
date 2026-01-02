#!/usr/bin/env python3
"""Test session creation and messaging."""
import asyncio
import httpx
import json

async def test_full_session():
    """Test creating a session and having a conversation."""
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
                if response.status_code == 200:
                    result = response.json()
                    user_msg = result.get('user_message', {})
                    ai_msg = result.get('ai_message', {})

                    print(f"✅ User message: {user_msg.get('content', 'N/A')}")
                    print(f"🤖 AI response: {ai_msg.get('content', 'N/A')[:150]}...")

                    # Check updated session
                    session_resp = await client.get(f"http://localhost:8000/api/v1/sessions/{session_id}", headers=headers)
                    if session_resp.status_code == 200:
                        updated_session = session_resp.json()
                        print(f"   Updated client info: {updated_session.get('client_info', {})}")

                else:
                    print(f"❌ Error: {response.text}")

            else:
                print(f"❌ Session creation failed: {response.text}")

    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_session())