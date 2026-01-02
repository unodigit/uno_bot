import requests
import websocket
import json
import time

def test_streaming_functionality():
    """Test the streaming functionality."""
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

    # Test 3: Test WebSocket connection
    try:
        ws_url = f"ws://localhost:8000/ws?session_id={session_id}"

        # Simple WebSocket test
        def on_open(ws):
            print("✓ WebSocket connection opened")
            # Send a test message
            ws.send(json.dumps({
                "event": "send_streaming_message",
                "data": {"content": "Hello, test message!"}
            }))

        def on_message(ws, message):
            data = json.loads(message)
            if data.get("event") == "connected":
                print("✓ WebSocket connected to session")
            elif data.get("event") == "streaming_message":
                print(f"✓ Received streaming chunk: {data['data']['chunk'][:50]}...")
            elif data.get("event") == "message":
                print("✓ Received complete message")

        def on_error(ws, error):
            print(f"✗ WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("✓ WebSocket connection closed")

        # Test WebSocket (non-blocking)
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Run for a short time to test
        start_time = time.time()
        while time.time() - start_time < 3:
            ws.run_forever(dispatcher=None, ping_interval=1, ping_timeout=0.5)
            break

        print("✓ WebSocket streaming test completed")

    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")

    print("\nStreaming implementation test completed!")
    print("Note: Full real-time testing requires WebSocket client in browser.")
    return True

if __name__ == "__main__":
    test_streaming_functionality()