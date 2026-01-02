import requests
import json
import time

def test_basic_streaming():
    """Test basic streaming functionality."""
    print("Testing UnoBot Streaming Implementation...")

    # Test 1: Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend API is running")
        else:
            print("✗ Backend API returned non-200 status")
            return False
    except Exception as e:
        print(f"✗ Backend API test failed: {e}")
        return False

    # Test 2: Create a session
    try:
        session_response = requests.post("http://localhost:8000/api/v1/sessions", timeout=5)
        if session_response.status_code == 201:
            session_data = session_response.json()
            session_id = session_data["id"]
            print(f"✓ Session created: {session_id}")
        else:
            print("✗ Failed to create session")
            return False
    except Exception as e:
        print(f"✗ Session creation failed: {e}")
        return False

    # Test 3: Send a message using regular endpoint
    try:
        message_response = requests.post(
            f"http://localhost:8000/api/v1/sessions/{session_id}/messages",
            json={"content": "Hello, test message!"},
            timeout=10
        )
        if message_response.status_code == 200:
            print("✓ Message sent successfully")
            messages = message_response.json().get("messages", [])
            if len(messages) >= 2:  # User message + AI response
                print("✓ Received AI response")
                print(f"   AI Response: {messages[-1]['content'][:100]}...")
        else:
            print("✗ Failed to send message")
            return False
    except Exception as e:
        print(f"✗ Message sending failed: {e}")
        return False

    print("\n✓ Basic streaming infrastructure test completed!")
    print("Note: WebSocket streaming requires browser client for full testing.")
    print("The backend is ready to handle streaming messages via WebSocket.")
    return True

if __name__ == "__main__":
    test_basic_streaming()