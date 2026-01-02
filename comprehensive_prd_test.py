#!/usr/bin/env python3
"""
Comprehensive test report for PRD endpoints.
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class PRDEndpointReport:
    def __init__(self):
        self.test_results = []
        self.session_id = None
        self.prd_id = None

    async def run_comprehensive_test(self):
        """Run comprehensive tests and generate report."""
        print("=" * 80)
        print("COMPREHENSIVE PRD ENDPOINTS TEST REPORT")
        print("=" * 80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {BASE_URL}")
        print()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Health Check
            result = await self.test_health_check(client)
            self.test_results.append(result)

            # Test 2: Session Creation
            result = await self.test_session_creation(client)
            self.test_results.append(result)

            # Test 3: Session Update
            if self.session_id:
                result = await self.test_session_update(client)
                self.test_results.append(result)

            # Test 4: PRD Generation
            if self.session_id:
                result = await self.test_prd_generation(client)
                self.test_results.append(result)

            # Test 5: PRD Preview
            if self.prd_id:
                result = await self.test_prd_preview(client)
                self.test_results.append(result)

            # Test 6: PRD Download
            if self.prd_id:
                result = await self.test_prd_download(client)
                self.test_results.append(result)

            # Test 7: Get PRD by Session
            if self.session_id:
                result = await self.test_get_prd_by_session(client)
                self.test_results.append(result)

        # Generate Final Report
        self.generate_final_report()

    async def test_health_check(self, client):
        """Test health check endpoint."""
        print("🧪 Test 1: Health Check")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            success = response.status_code == 200
            if success:
                data = response.json()
                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   📊 Response: {data}")
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
            return {
                "test": "Health Check",
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "Health Check",
                "status": "FAIL",
                "error": str(e)
            }

    async def test_session_creation(self, client):
        """Test session creation."""
        print("🧪 Test 2: Session Creation")
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

            response = await client.post(
                f"{BASE_URL}/api/v1/sessions",
                json=session_data,
                headers=HEADERS
            )

            success = response.status_code == 201
            if success:
                data = response.json()
                self.session_id = data["id"]
                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   🆔 Session ID: {self.session_id}")
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
            return {
                "test": "Session Creation",
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "session_id": self.session_id if success else None,
                "response": response.json() if success else response.text
            }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "Session Creation",
                "status": "FAIL",
                "error": str(e)
            }

    async def test_session_update(self, client):
        """Test session data update."""
        print("🧪 Test 3: Session Data Update")
        try:
            update_data = {
                "client_info": {
                    "name": "Updated Test Client",
                    "email": "updated@example.com",
                    "company": "Updated Test Company"
                },
                "business_context": {
                    "challenges": "We need to implement AI-powered customer onboarding with automation",
                    "goals": "Reduce onboarding time from 2 weeks to 2 days with 90%+ customer satisfaction",
                    "current_technology": "Manual processes with basic CRM",
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

            response = await client.patch(
                f"{BASE_URL}/api/v1/sessions/{self.session_id}",
                json=update_data,
                headers=HEADERS
            )

            success = response.status_code == 200
            if success:
                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   📊 Session updated successfully")
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
            return {
                "test": "Session Update",
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "Session Update",
                "status": "FAIL",
                "error": str(e)
            }

    async def test_prd_generation(self, client):
        """Test PRD generation."""
        print("🧪 Test 4: PRD Generation")
        try:
            prd_data = {
                "session_id": self.session_id
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/prd/generate",
                json=prd_data,
                headers=HEADERS
            )

            success = response.status_code == 201
            if success:
                data = response.json()
                self.prd_id = data["id"]
                content_length = len(data.get("content_markdown", ""))
                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   🆔 PRD ID: {self.prd_id}")
                print(f"   📄 Content Length: {content_length} characters")
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
            return {
                "test": "PRD Generation",
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "prd_id": self.prd_id if success else None,
                "content_length": content_length if success else 0,
                "response": response.json() if success else response.text
            }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "PRD Generation",
                "status": "FAIL",
                "error": str(e)
            }

    async def test_prd_preview(self, client):
        """Test PRD preview."""
        print("🧪 Test 5: PRD Preview")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/prd/{self.prd_id}/preview",
                headers=HEADERS
            )

            success = response.status_code == 200
            if success:
                data = response.json()
                preview_length = len(data.get("preview_text", ""))
                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   📄 Filename: {data.get('filename', 'N/A')}")
                print(f"   👁️ Preview Length: {preview_length} characters")
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
            return {
                "test": "PRD Preview",
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "preview_length": preview_length if success else 0,
                "response": response.json() if success else response.text
            }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "PRD Preview",
                "status": "FAIL",
                "error": str(e)
            }

    async def test_prd_download(self, client):
        """Test PRD download."""
        print("🧪 Test 6: PRD Download")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/prd/{self.prd_id}/download",
                headers=HEADERS
            )

            success = response.status_code == 200
            if success:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                content_length = len(response.text)

                is_markdown = 'text/markdown' in content_type
                has_filename = 'filename=' in content_disposition

                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📁 Content-Disposition: {content_disposition}")
                print(f"   📊 Content Length: {content_length} characters")
                print(f"   ✅ Is Markdown: {is_markdown}")
                print(f"   ✅ Has Filename: {has_filename}")

                # Verify markdown content
                content = response.text
                has_title = any(line.startswith('#') for line in content.split('\n')[:10])
                has_sections = sum(1 for line in content.split('\n') if line.startswith('##')) >= 3

                print(f"   ✅ Has Title: {has_title}")
                print(f"   ✅ Has Sections: {has_sections}")

                overall_success = is_markdown and has_filename and has_title and has_sections
                return {
                    "test": "PRD Download",
                    "status": "PASS" if overall_success else "FAIL",
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "content_length": content_length,
                    "is_markdown": is_markdown,
                    "has_filename": has_filename,
                    "has_title": has_title,
                    "has_sections": has_sections
                }
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                return {
                    "test": "PRD Download",
                    "status": "FAIL",
                    "status_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "PRD Download",
                "status": "FAIL",
                "error": str(e)
            }

    async def test_get_prd_by_session(self, client):
        """Test get PRD by session."""
        print("🧪 Test 7: Get PRD by Session")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/prd/session/{self.session_id}",
                headers=HEADERS
            )

            success = response.status_code == 200
            if success:
                data = response.json()
                prd_id_from_session = data.get("id")
                print(f"   ✅ PASS - Status: {response.status_code}")
                print(f"   🆔 PRD ID from Session: {prd_id_from_session}")
                print(f"   ✅ Matches Generated PRD: {prd_id_from_session == self.prd_id}")
            else:
                print(f"   ❌ FAIL - Status: {response.status_code}")
                print(f"   📝 Error: {response.text}")
            return {
                "test": "Get PRD by Session",
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "response": response.json() if success else response.text
            }
        except Exception as e:
            print(f"   ❌ FAIL - Exception: {e}")
            return {
                "test": "Get PRD by Session",
                "status": "FAIL",
                "error": str(e)
            }

    def generate_final_report(self):
        """Generate final test report."""
        print("\n" + "=" * 80)
        print("FINAL TEST RESULTS")
        print("=" * 80)

        passed_tests = sum(1 for result in self.test_results if result.get("status") == "PASS")
        total_tests = len(self.test_results)

        for i, result in enumerate(self.test_results, 1):
            status = result.get("status", "FAIL")
            status_symbol = "✅" if status == "PASS" else "❌"
            test_name = result.get("test", f"Test {i}")
            print(f"{status_symbol} {test_name}: {status}")

        print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! The PRD endpoints are working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")

        print("\n" + "=" * 80)
        print("DETAILED RESULTS")
        print("=" * 80)

        for result in self.test_results:
            print(f"\nTest: {result.get('test', 'Unknown')}")
            print(f"Status: {result.get('status', 'FAIL')}")
            if 'status_code' in result:
                print(f"Status Code: {result['status_code']}")
            if 'error' in result:
                print(f"Error: {result['error']}")
            if 'response' in result:
                print(f"Response: {json.dumps(result['response'], indent=2)}")

        # Save report to file
        report_data = {
            "test_date": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "summary": {
                "passed": passed_tests,
                "total": total_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
            },
            "results": self.test_results
        }

        with open("/media/DATA/projects/autonomous-coding-uno-bot/unobot/prd_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: prd_test_report.json")


async def main():
    """Main test function."""
    tester = PRDEndpointReport()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())