#!/usr/bin/env python3
"""Simple test to debug the issue."""
import asyncio
import httpx

async def simple_test():
    """Simple step-by-step test."""
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Create session
            print("Step 1: Creating session...")
            session_data = {"visitor_id": "test_visitor_123"}
            response = await client.post("http://localhost:8000/api/v1/sessions", json=session_data)
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}...")

            if response.status_code == 201:
                session = response.json()
                session_id = session.get('id')
                print(f"  ✅ Session ID: {session_id}")

                # Step 2: Send message
                print("\nStep 2: Sending message...")
                message_data = {"content": "Hello"}
                headers = {"X-Session-ID": session_id}

                response = await client.post(
                    f"http://localhost:8000/api/v1/sessions/{session_id}/messages",
                    json=message_data,
                    headers=headers
                )
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}...")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(simple_test())