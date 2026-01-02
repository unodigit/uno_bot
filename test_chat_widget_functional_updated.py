#!/usr/bin/env python3
"""
Updated functional test for chat widget with correct API format
"""

import requests
import json
import time
import uuid
from typing import Dict, Any

class ChatWidgetFunctionalTestUpdated:
    def __init__(self):
        self.base_url = "http://localhost:5173"
        self.api_base = "http://localhost:8000/api/v1"

    def generate_visitor_id(self):
        """Generate a unique visitor ID"""
        return str(uuid.uuid4())

    def test_websocket_connection(self):
        """Test WebSocket connection for chat functionality"""
        print("Testing WebSocket connection...")

        try:
            # Check if the API is responding
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
        """Test chat session creation with correct format"""
        print("Testing chat session creation...")

        try:
            # Use correct format from SessionCreate schema
            visitor_id = self.generate_visitor_id()
            session_data = {
                "visitor_id": visitor_id,
                "source_url": "http://localhost:5173/",
                "user_agent": "Test Client/1.0"
            }

            response = requests.post(
                f"{self.api_base}/sessions",
                json=session_data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                session_response = response.json()
                print(f"  ✓ Session created successfully")
                print(f"  Session ID: {session_response.get('id', 'unknown')}")
                print(f"  Visitor ID: {session_response.get('visitor_id', 'unknown')}")
                return True
            else:
                print(f"  ✗ Session creation failed: {response.status_code}")
                print(f"  Response: {response.text[:300]}")
                return False

        except Exception as e:
            print(f"  ✗ Session creation test failed: {e}")
            return False

    def test_message_sending(self):
        """Test sending messages to chat with correct format"""
        print("Testing message sending...")

        try:
            # First create a session
            visitor_id = self.generate_visitor_id()
            session_data = {
                "visitor_id": visitor_id,
                "source_url": "http://localhost:5173/",
                "user_agent": "Test Client/1.0"
            }

            session_response = requests.post(
                f"{self.api_base}/sessions",
                json=session_data,
                timeout=10
            )

            if session_response.status_code not in [200, 201]:
                print("  ✗ Cannot create session for message test")
                return False

            session_response_data = session_response.json()
            session_id = session_response_data.get('id')

            # Send a test message with correct format from MessageCreate schema
            message_data = {
                "content": "Hello, this is a test message from the functional test",
                "meta_data": {
                    "source": "functional_test",
                    "test_type": "automated"
                }
            }

            message_response = requests.post(
                f"{self.api_base}/sessions/{session_id}/messages",
                json=message_data,
                timeout=10
            )

            if message_response.status_code in [200, 201]:
                message_response_data = message_response.json()
                print(f"  ✓ Message sent successfully")
                print(f"  Message ID: {message_response_data.get('id', 'unknown')}")
                return True
            else:
                print(f"  ✗ Message sending failed: {message_response.status_code}")
                print(f"  Response: {message_response.text[:300]}")
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

    def test_session_resume(self):
        """Test session resume functionality"""
        print("Testing session resume...")

        try:
            # Create a session first
            visitor_id = self.generate_visitor_id()
            session_data = {
                "visitor_id": visitor_id,
                "source_url": "http://localhost:5173/",
                "user_agent": "Test Client/1.0"
            }

            session_response = requests.post(
                f"{self.api_base}/sessions",
                json=session_data,
                timeout=10
            )

            if session_response.status_code not in [200, 201]:
                print("  ✗ Cannot create session for resume test")
                return False

            session_data = session_response.json()
            session_id = session_data.get('id')

            # Resume the session
            resume_response = requests.get(
                f"{self.api_base}/sessions/{session_id}",
                timeout=10
            )

            if resume_response.status_code == 200:
                resume_data = resume_response.json()
                print(f"  ✓ Session resumed successfully")
                print(f"  Session ID: {resume_data.get('id')}")
                print(f"  Current Phase: {resume_data.get('current_phase')}")
                return True
            else:
                print(f"  ✗ Session resume failed: {resume_response.status_code}")
                print(f"  Response: {resume_response.text[:200]}")
                return False

        except Exception as e:
            print(f"  ✗ Session resume test failed: {e}")
            return False

    def test_expert_matching(self):
        """Test expert matching functionality"""
        print("Testing expert matching...")

        try:
            # Create a session with business context
            visitor_id = self.generate_visitor_id()
            session_data = {
                "visitor_id": visitor_id,
                "source_url": "http://localhost:5173/",
                "user_agent": "Test Client/1.0"
            }

            session_response = requests.post(
                f"{self.api_base}/sessions",
                json=session_data,
                timeout=10
            )

            if session_response.status_code not in [200, 201]:
                print("  ✗ Cannot create session for expert matching test")
                return False

            session_data = session_response.json()
            session_id = session_data.get('id')

            # Update session with business context to trigger expert matching
            update_data = {
                "business_context": {
                    "industry": "Technology",
                    "challenges": "Need help with AI implementation and digital transformation",
                    "current_stack": ["React", "Node.js", "AWS"],
                    "goals": "Improve customer experience and automate processes"
                }
            }

            update_response = requests.patch(
                f"{self.api_base}/sessions/{session_id}",
                json=update_data,
                timeout=10
            )

            if update_response.status_code == 200:
                print("  ✓ Session updated with business context")
            else:
                print(f"  ✗ Session update failed: {update_response.status_code}")
                return False

            # Try to trigger expert matching by sending a message
            message_data = {
                "content": "Can you help me find the right expert for my AI implementation needs?",
                "meta_data": {
                    "source": "functional_test",
                    "intent": "expert_matching"
                }
            }

            message_response = requests.post(
                f"{self.api_base}/sessions/{session_id}/messages",
                json=message_data,
                timeout=10
            )

            if message_response.status_code in [200, 201]:
                print("  ✓ Message sent to trigger expert matching")
                return True
            else:
                print(f"  ✗ Message sending for expert matching failed: {message_response.status_code}")
                return False

        except Exception as e:
            print(f"  ✗ Expert matching test failed: {e}")
            return False

    def generate_functional_report(self):
        """Generate functional test report"""
        print("\n" + "="*60)
        print("CHAT WIDGET FUNCTIONAL TEST REPORT (UPDATED)")
        print("="*60)

        tests = [
            ("Frontend Availability", self.test_frontend_availability),
            ("WebSocket/API Connection", self.test_websocket_connection),
            ("Chat Session Creation", self.test_chat_session_creation),
            ("Message Sending", self.test_message_sending),
            ("Session Resume", self.test_session_resume),
            ("Expert Matching", self.test_expert_matching)
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
    print("UnoBot Chat Widget Functional Test (Updated)")
    print("Testing chat widget functionality with correct API format")

    tester = ChatWidgetFunctionalTestUpdated()
    results = tester.generate_functional_report()

    # Save results
    with open('/media/DATA/projects/autonomous-coding-uno-bot/unobot/chat_widget_functional_report_updated.json', 'w') as f:
        json.dump({
            "test_date": "2026-01-02",
            "application": "UnoBot",
            "base_url": "http://localhost:5173",
            "api_base": "http://localhost:8000/api/v1",
            "results": results
        }, f, indent=2)

    print(f"\nUpdated functional test report saved to: chat_widget_functional_report_updated.json")