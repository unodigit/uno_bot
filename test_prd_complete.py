#!/usr/bin/env python3
"""
Updated test script for PRD generation endpoints.
Tests the three critical PRD endpoints with proper session data setup:
1. POST /api/v1/sessions/{id}/prd - generates document
2. GET /api/v1/prd/{id}/download - returns markdown file
3. GET /api/v1/prd/{id}/preview - returns PRD preview
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class PRDEndpointTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_id: Optional[str] = None
        self.prd_id: Optional[str] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def test_health_check(self) -> bool:
        """Test if the API is running."""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/health")
            print(f"Health Check - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Health Check - Response: {response.json()}")
                return True
            else:
                print(f"Health Check - Error: {response.text}")
                return False
        except Exception as e:
            print(f"Health Check - Exception: {e}")
            return False

    async def create_test_session(self) -> bool:
        """Create a test session with complete data for PRD generation."""
        try:
            session_data = {
                "visitor_id": f"test_visitor_{datetime.now().isoformat()}",
                "source_url": "http://localhost:5173/test",
                "user_agent": "Test Script",
                "client_info": {
                    "name": "Test Client",
                    "email": "test@example.com",
                    "company": "Test Company"
                },
                "business_context": {
                    "challenges": "We need to improve our customer onboarding process",
                    "goals": "Reduce onboarding time and improve user experience",
                    "current_technology": "Currently using manual processes",
                    "industry": "SaaS"
                },
                "qualification": {
                    "budget_range": "50000-100000",
                    "timeline": "3-6 months",
                    "decision_maker": True,
                    "business_size": "50-200 employees"
                },
                "recommended_service": "AI Strategy Consulting"
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/sessions",
                json=session_data,
                headers=HEADERS
            )

            print(f"Create Session - Status: {response.status_code}")
            if response.status_code == 201:
                session_response = response.json()
                self.session_id = session_response["id"]
                print(f"Create Session - Success: Session ID {self.session_id}")
                return True
            else:
                print(f"Create Session - Error: {response.text}")
                return False

        except Exception as e:
            print(f"Create Session - Exception: {e}")
            return False

    async def update_session_with_complete_data(self) -> bool:
        """Update session with complete data required for PRD generation."""
        if not self.session_id:
            print("Update Session - Error: No session ID available")
            return False

        try:
            # Update session with complete business context and qualification
            update_data = {
                "client_info": {
                    "name": "Test Client Updated",
                    "email": "test@example.com",
                    "company": "Test Company Inc."
                },
                "business_context": {
                    "challenges": "We need to improve our customer onboarding process by implementing AI-powered solutions",
                    "goals": "Reduce onboarding time from 2 weeks to 2 days and improve user experience",
                    "current_technology": "Currently using manual processes with basic CRM",
                    "industry": "SaaS",
                    "pain_points": ["Manual data entry", "Slow response times", "Poor user experience"],
                    "success_criteria": ["Faster onboarding", "Better user satisfaction", "Reduced support tickets"]
                },
                "qualification": {
                    "budget_range": "50000-100000",
                    "timeline": "3-6 months",
                    "decision_maker": True,
                    "business_size": "50-200 employees",
                    "technical_comfort": "Medium",
                    "urgency": "High"
                },
                "lead_score": 85,
                "recommended_service": "AI Strategy Consulting"
            }

            response = await self.client.patch(
                f"{self.base_url}/api/v1/sessions/{self.session_id}",
                json=update_data,
                headers=HEADERS
            )

            print(f"Update Session - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Update Session - Success: Session updated with complete data")
                return True
            else:
                print(f"Update Session - Error: {response.text}")
                return False

        except Exception as e:
            print(f"Update Session - Exception: {e}")
            return False

    async def generate_prd(self) -> bool:
        """Test PRD generation endpoint."""
        if not self.session_id:
            print("Generate PRD - Error: No session ID available")
            return False

        try:
            prd_data = {
                "session_id": self.session_id
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/prd/generate",
                json=prd_data,
                headers=HEADERS
            )

            print(f"Generate PRD - Status: {response.status_code}")
            if response.status_code == 201:
                prd_response = response.json()
                self.prd_id = prd_response["id"]
                print(f"Generate PRD - Success: PRD ID {self.prd_id}")
                print(f"Generate PRD - Content length: {len(prd_response.get('content_markdown', ''))}")
                return True
            else:
                print(f"Generate PRD - Error: {response.text}")
                return False

        except Exception as e:
            print(f"Generate PRD - Exception: {e}")
            return False

    async def test_prd_preview(self) -> bool:
        """Test PRD preview endpoint."""
        if not self.prd_id:
            print("Preview PRD - Error: No PRD ID available")
            return False

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/prd/{self.prd_id}/preview",
                headers=HEADERS
            )

            print(f"Preview PRD - Status: {response.status_code}")
            if response.status_code == 200:
                preview_response = response.json()
                print(f"Preview PRD - Success: Preview available")
                print(f"Preview PRD - Filename: {preview_response.get('filename')}")
                print(f"Preview PRD - Preview text length: {len(preview_response.get('preview_text', ''))}")
                return True
            else:
                print(f"Preview PRD - Error: {response.text}")
                return False

        except Exception as e:
            print(f"Preview PRD - Exception: {e}")
            return False

    async def test_prd_download(self) -> bool:
        """Test PRD download endpoint."""
        if not self.prd_id:
            print("Download PRD - Error: No PRD ID available")
            return False

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/prd/{self.prd_id}/download",
                headers=HEADERS
            )

            print(f"Download PRD - Status: {response.status_code}")
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')

                print(f"Download PRD - Content-Type: {content_type}")
                print(f"Download PRD - Content-Disposition: {content_disposition}")

                # Check if it's markdown
                if 'text/markdown' in content_type:
                    content = response.text
                    print(f"Download PRD - Success: Markdown file downloaded")
                    print(f"Download PRD - Content length: {len(content)}")
                    print(f"Download PRD - First 200 chars: {content[:200]}")
                    return True
                else:
                    print(f"Download PRD - Error: Wrong content type: {content_type}")
                    return False
            else:
                print(f"Download PRD - Error: {response.text}")
                return False

        except Exception as e:
            print(f"Download PRD - Exception: {e}")
            return False

    async def test_prd_by_session(self) -> bool:
        """Test getting PRD by session ID."""
        if not self.session_id:
            print("Get PRD by Session - Error: No session ID available")
            return False

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/prd/session/{self.session_id}",
                headers=HEADERS
            )

            print(f"Get PRD by Session - Status: {response.status_code}")
            if response.status_code == 200:
                prd_response = response.json()
                print(f"Get PRD by Session - Success: PRD found for session")
                print(f"Get PRD by Session - PRD ID: {prd_response.get('id')}")
                return True
            else:
                print(f"Get PRD by Session - Error: {response.text}")
                return False

        except Exception as e:
            print(f"Get PRD by Session - Exception: {e}")
            return False

    async def run_all_tests(self):
        """Run all PRD endpoint tests."""
        print("=" * 60)
        print("PRD Endpoints Test Suite")
        print("=" * 60)

        # Test 1: Health check
        print("\n1. Testing Health Check...")
        health_ok = await self.test_health_check()

        # Test 2: Create session
        print("\n2. Testing Session Creation...")
        session_ok = await self.create_test_session()

        # Test 3: Update session with complete data
        print("\n3. Testing Session Data Update...")
        update_ok = await self.update_session_with_complete_data()

        # Test 4: Generate PRD
        print("\n4. Testing PRD Generation...")
        prd_ok = await self.generate_prd()

        # Test 5: Preview PRD
        print("\n5. Testing PRD Preview...")
        preview_ok = await self.test_prd_preview()

        # Test 6: Download PRD
        print("\n6. Testing PRD Download...")
        download_ok = await self.test_prd_download()

        # Test 7: Get PRD by session
        print("\n7. Testing Get PRD by Session...")
        session_prd_ok = await self.test_prd_by_session()

        # Summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Health Check:              {'✓ PASS' if health_ok else '✗ FAIL'}")
        print(f"Session Creation:          {'✓ PASS' if session_ok else '✗ FAIL'}")
        print(f"Session Data Update:       {'✓ PASS' if update_ok else '✗ FAIL'}")
        print(f"PRD Generation:            {'✓ PASS' if prd_ok else '✗ FAIL'}")
        print(f"PRD Preview:               {'✓ PASS' if preview_ok else '✗ FAIL'}")
        print(f"PRD Download:              {'✓ PASS' if download_ok else '✗ FAIL'}")
        print(f"Get PRD by Session:        {'✓ PASS' if session_prd_ok else '✗ FAIL'}")

        all_passed = all([health_ok, session_ok, update_ok, prd_ok, preview_ok, download_ok, session_prd_ok])
        print(f"\nOverall Result:            {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

        return all_passed


async def main():
    """Main test function."""
    async with PRDEndpointTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())