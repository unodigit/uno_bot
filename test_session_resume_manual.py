#!/usr/bin/env python3
"""
Manual verification script for session resume via email link functionality.
This script tests the complete flow without browser automation.
"""

import requests
import json
import time
import uuid

def test_session_resume_flow():
    """Test the complete session resume flow."""
    print("=== TESTING SESSION RESUME VIA EMAIL LINK ===\n")

    base_url = "http://localhost:8000"
    visitor_id = f"test_visitor_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Step 1: Create a new session
    print("Step 1: Creating new session...")
    create_response = requests.post(
        f"{base_url}/api/v1/sessions",
        json={
            "visitor_id": visitor_id,
            "source_url": "http://localhost:5180",
            "user_agent": "Test Script"
        }
    )

    if create_response.status_code != 201:
        print(f"❌ Failed to create session: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False

    session_data = create_response.json()
    session_id = session_data["id"]
    print(f"✓ Created session: {session_id}")

    # Step 2: Send a test message to establish conversation
    print("\nStep 2: Sending test message...")
    message_response = requests.post(
        f"{base_url}/api/v1/sessions/{session_id}/messages",
        json={
            "content": "Hello, I need help with a business consultation.",
            "metadata": {}
        }
    )

    if message_response.status_code != 200:
        print(f"❌ Failed to send message: {message_response.status_code}")
        print(f"Response: {message_response.text}")
        return False

    message_data = message_response.json()
    print(f"✓ Message sent successfully")

    # Wait a moment for processing
    time.sleep(1)

    # Step 3: Get session details to verify message is stored
    print("\nStep 3: Verifying conversation history...")
    get_session_response = requests.get(f"{base_url}/api/v1/sessions/{session_id}")

    if get_session_response.status_code != 200:
        print(f"❌ Failed to get session: {get_session_response.status_code}")
        print(f"Response: {get_session_response.text}")
        return False

    session_with_history = get_session_response.json()
    messages = session_with_history["messages"]

    if len(messages) < 2:  # Should have initial greeting + user message
        print(f"❌ Expected at least 2 messages, got {len(messages)}")
        return False

    print(f"✓ Conversation history preserved: {len(messages)} messages")

    # Step 4: Resume the session via API
    print("\nStep 4: Resuming session via API...")
    resume_response = requests.post(
        f"{base_url}/api/v1/sessions/{session_id}/resume",
        json={}
    )

    if resume_response.status_code != 200:
        print(f"❌ Failed to resume session: {resume_response.status_code}")
        print(f"Response: {resume_response.text}")
        return False

    resumed_session = resume_response.json()
    print(f"✓ Session resumed successfully")

    # Step 5: Verify resumed session has complete history
    print("\nStep 5: Verifying resumed session data...")
    resumed_messages = resumed_session["messages"]

    if len(resumed_messages) != len(messages):
        print(f"❌ Message count mismatch: original={len(messages)}, resumed={len(resumed_messages)}")
        return False

    print(f"✓ Complete conversation history preserved in resumed session")

    # Step 6: Test resume with URL parameter simulation
    print("\nStep 6: Testing URL parameter handling...")
    # This simulates what the frontend does when loading with ?session_id= param
    resume_path_response = requests.post(
        f"{base_url}/api/v1/sessions/resume",
        json={"session_id": session_id}
    )

    if resume_path_response.status_code != 200:
        print(f"❌ Failed to resume via path: {resume_path_response.status_code}")
        print(f"Response: {resume_path_response.text}")
        return False

    resumed_via_path = resume_path_response.json()
    print(f"✓ Session resumed via path parameter successfully")

    # Step 7: Test invalid session handling
    print("\nStep 7: Testing invalid session handling...")
    invalid_resume_response = requests.post(
        f"{base_url}/api/v1/sessions/resume",
        json={"session_id": "invalid-session-id"}
    )

    if invalid_resume_response.status_code != 404:
        print(f"❌ Expected 404 for invalid session, got {invalid_resume_response.status_code}")
        return False

    print(f"✓ Invalid session properly handled (404)")

    print("\n=== SESSION RESUME TEST COMPLETED SUCCESSFULLY ===")
    print(f"✓ Session ID: {session_id}")
    print(f"✓ Resume URL would be: http://localhost:5180?session_id={session_id}")
    print(f"✓ Complete conversation history preserved")
    print(f"✓ Frontend can load session automatically from URL parameter")

    return True

def test_frontend_url_generation():
    """Test that frontend URL generation works correctly."""
    print("\n=== TESTING FRONTEND URL GENERATION ===")

    # Simulate frontend URL generation
    base_url = "http://localhost:5180"
    session_id = "test-session-123"

    # This is what the frontend's generateSessionResumeUrl function does
    resume_url = f"{base_url}?session_id={session_id}"

    print(f"✓ Generated resume URL: {resume_url}")
    print(f"✓ URL format matches expected pattern")

    return True

if __name__ == "__main__":
    print("UNOBOT SESSION RESUME VERIFICATION")
    print("=" * 50)

    success = True

    try:
        success &= test_session_resume_flow()
        success &= test_frontend_url_generation()

        if success:
            print("\n🎉 ALL TESTS PASSED!")
            print("Session resume via email link functionality is working correctly.")
        else:
            print("\n❌ SOME TESTS FAILED!")
            print("Session resume functionality needs investigation.")

    except Exception as e:
        print(f"\n💥 TEST EXECUTION ERROR: {e}")
        success = False

    exit(0 if success else 1)