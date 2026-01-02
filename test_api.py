#!/usr/bin/env python3
import requests
import json

def test_api_endpoints():
    """Test various API endpoints to verify functionality."""

    print("=== Testing API Endpoints ===")

    # Test session creation
    print("\n1. Testing session creation...")
    session_data = {
        'visitor_id': 'test-visitor-api',
        'source_url': 'http://localhost:5173/test',
        'user_agent': 'Test Client'
    }

    response = requests.post('http://localhost:8000/api/v1/sessions', json=session_data)
    print(f"Session creation: {response.status_code}")

    if response.status_code == 201:
        session_response = response.json()
        session_id = session_response['id']
        print(f"Created session: {session_id}")

        # Test getting session
        print("\n2. Testing get session...")
        response = requests.get(f'http://localhost:8000/api/v1/sessions/{session_id}')
        print(f"Get session: {response.status_code}")

        if response.status_code == 200:
            session_data = response.json()
            print(f"Session phase: {session_data.get('current_phase')}")
            print(f"Messages count: {len(session_data.get('messages', []))}")

        # Test sending a message
        print("\n3. Testing send message...")
        message_data = {'content': 'Hello from API test'}
        response = requests.post(
            f'http://localhost:8000/api/v1/sessions/{session_id}/messages',
            json=message_data
        )
        print(f"Send message: {response.status_code}")

        if response.status_code == 201:
            message_response = response.json()
            print(f"Message sent: {message_response['id']}")

        # Test expert listing
        print("\n4. Testing expert listing...")
        response = requests.get('http://localhost:8000/api/v1/experts')
        print(f"Get experts: {response.status_code}")

        if response.status_code == 200:
            experts = response.json()
            print(f"Found {len(experts)} experts")
            if experts:
                print(f"First expert: {experts[0].get('name')}")

        # Test admin expert listing
        print("\n5. Testing admin expert listing...")
        response = requests.get('http://localhost:8000/api/v1/admin/experts')
        print(f"Admin experts: {response.status_code}")

        # Test health check
        print("\n6. Testing health check...")
        response = requests.get('http://localhost:8000/api/v1/health')
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")

        # Test OpenAPI docs
        print("\n7. Testing OpenAPI documentation...")
        response = requests.get('http://localhost:8000/docs')
        print(f"OpenAPI docs: {response.status_code}")

        # Test ReDoc
        print("\n8. Testing ReDoc...")
        response = requests.get('http://localhost:8000/redoc')
        print(f"ReDoc: {response.status_code}")

    else:
        print(f"Session creation failed: {response.text}")

    print("\n=== API Tests Complete ===")

if __name__ == "__main__":
    test_api_endpoints()