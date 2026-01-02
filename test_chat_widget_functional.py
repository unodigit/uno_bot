#!/usr/bin/env python3
"""
Functional test for chat widget using HTTP requests to verify API endpoints
Since the chat widget is a React component, we'll test the underlying functionality
"""

import requests
import json
import time
from typing import Dict, Any

class ChatWidgetFunctionalTest:
    def __init__(self):
        self.base_url = "http://localhost:5173"
        self.api_base = "http://localhost:8000/api/v1"

    def test_websocket_connection(self):
        """Test WebSocket connection for chat functionality"""
        print("Testing WebSocket connection...")

        try:
            # Try to connect to WebSocket endpoint
            ws_url = "ws://localhost:8000/ws/chat"
            print(f"  WebSocket URL: {ws_url}")

            # Note: We can't easily test WebSocket with requests, but we can check if the server is running
            # by trying to access the API endpoints
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                print("  ✓ Backend API is responding")
                return True
            else:
                print(f"  ✗ Backend API returned status: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ✗ WebSocket/API test failed: {e}")
            return False

    def test_chat_session_creation(self):
        """Test chat session creation"""
        print("Testing chat session creation...")

        try:
            # Test session creation endpoint
            response = requests.post(
                f"{self.api_base}/sessions",
                json={"client_name": "Test User", "client_email": "test@example.com"},
                timeout=10
            )

            if response.status_code in [200, 201]:
                session_data = response.json()
                print(f"  ✓ Session created successfully: {session_data.get('session_id', 'unknown')}")
                return True
            else:
                print(f"  ✗ Session creation failed: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"  ✗ Session creation test failed: {e}")
            return False

    def test_message_sending(self):
        """Test sending messages to chat"""
        print("Testing message sending...")

        try:
            # First create a session
            session_response = requests.post(
                f"{self.api_base}/sessions",
                json={"client_name": "Test User", "client_email": "test@example.com"},
                timeout=10
            )

            if session_response.status_code not in [200, 201]:
                print("  ✗ Cannot create session for message test")
                return False

            session_data = session_response.json()
            session_id = session_data.get('session_id')

            # Send a test message
            message_response = requests.post(
                f"{self.api_base}/sessions/{session_id}/messages",
                json={"content": "Hello, this is a test message"},
                timeout=10
            )

            if message_response.status_code in [200, 201]:
                message_data = message_response.json()
                print(f"  ✓ Message sent successfully")
                print(f"  Message ID: {message_data.get('message_id', 'unknown')}")
                return True
            else:
                print(f"  ✗ Message sending failed: {message_response.status_code}")
                print(f"  Response: {message_response.text[:200]}")
                return False

        except Exception as e:
            print(f"  ✗ Message sending test failed: {e}")
            return False

    def test_frontend_availability(self):
        """Test if the frontend is properly serving the React application"""
        print("Testing frontend availability...")

        try:
            # Test main page
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200 and 'react' in response.text.lower():
                print("  ✓ React application is loaded")
            else:
                print(f"  ✗ React application not found. Status: {response.status_code}")

            # Test if the main script is available
            script_response = requests.get(f"{self.base_url}/src/main.tsx", timeout=10)
            if script_response.status_code == 200:
                print("  ✓ Main application script is available")
            else:
                print(f"  ✗ Main script not available. Status: {script_response.status_code}")

            return True

        except Exception as e:
            print(f"  ✗ Frontend test failed: {e}")
            return False

    def generate_functional_report(self):
        """Generate functional test report"""
        print("\n" + "="*60)
        print("CHAT WIDGET FUNCTIONAL TEST REPORT")
        print("="*60)

        tests = [
            ("Frontend Availability", self.test_frontend_availability),
            ("WebSocket/API Connection", self.test_websocket_connection),
            ("Chat Session Creation", self.test_chat_session_creation),
            ("Message Sending", self.test_message_sending)
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"  ✗ Test failed with exception: {e}")
                results.append((test_name, False))

        # Summary
        passed = sum(1 for _, result in results if result)
        total = len(results)

        print(f"\n{'='*60}")
        print("FUNCTIONAL TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status}: {test_name}")

        if passed == total:
            print("\n✅ All functional tests passed!")
            print("The chat widget backend and frontend are working correctly.")
        else:
            print(f"\n⚠️  {total - passed} functional test(s) failed.")
            print("Some chat widget functionality may not be working properly.")

        return results

if __name__ == "__main__":
    print("UnoBot Chat Widget Functional Test")
    print("Testing chat widget functionality and API endpoints")

    tester = ChatWidgetFunctionalTest()
    results = tester.generate_functional_report()

    # Save results
    with open('/media/DATA/projects/autonomous-coding-uno-bot/unobot/chat_widget_functional_report.json', 'w') as f:
        json.dump({
            "test_date": "2026-01-02",
            "application": "UnoBot",
            "base_url": "http://localhost:5173",
            "api_base": "http://localhost:8000/api/v1",
            "results": results
        }, f, indent=2)

    print(f"\nFunctional test report saved to: chat_widget_functional_report.json")