#!/usr/bin/env python3
"""
Admin Conversation Analytics E2E Test Runner

This script runs the comprehensive admin conversation analytics tests
and generates a detailed test report.
"""

import json
import subprocess
import sys
import time


def run_analytics_test_suite():
    """Run the admin conversation analytics test suite and capture results."""

    print("=" * 80)
    print("UNOBOT ADMIN CONVERSATION ANALYTICS - E2E TEST SUITE")
    print("=" * 80)
    print()

    # Test suite configuration
    test_file = "tests/e2e/test_admin_conversation_analytics.py"
    test_patterns = [
        "test_admin_dashboard_loads_successfully",
        "test_conversation_analytics_section_display",
        "test_conversation_analytics_metrics_display",
        "test_most_popular_service_display",
        "test_analytics_data_consistency",
        "test_analytics_section_responsive_design",
        "test_analytics_loading_states",
        "test_analytics_api_integration",
        "test_analytics_ui_interactions",
        "test_complete_analytics_verification"
    ]

    results = {
        "total_tests": len(test_patterns),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }

    print(f"Running {len(test_patterns)} tests from {test_file}")
    print("-" * 80)
    print()

    # Run each test individually to get detailed results
    for test_name in test_patterns:
        print(f"Running: {test_name}")
        print("-" * 60)

        try:
            # Run the specific test
            cmd = [
                sys.executable, "-m", "pytest",
                f"{test_file}::{test_name}",
                "-v", "-s", "--tb=short"
            ]

            result = subprocess.run(
                cmd,
                cwd="/media/DATA/projects/autonomous-coding-uno-bot/unobot",
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout per test
            )

            if result.returncode == 0:
                print(f"✓ PASSED: {test_name}")
                results["passed"] += 1
                results["details"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
            else:
                print(f"✗ FAILED: {test_name}")
                results["failed"] += 1
                results["details"].append({
                    "name": test_name,
                    "status": "FAILED",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })

        except subprocess.TimeoutExpired:
            print(f"⏱ TIMEOUT: {test_name}")
            results["failed"] += 1
            results["details"].append({
                "name": test_name,
                "status": "TIMEOUT",
                "stdout": "",
                "stderr": "Test timed out after 3 minutes"
            })

        except Exception as e:
            print(f"✗ ERROR: {test_name} - {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "name": test_name,
                "status": "ERROR",
                "stdout": "",
                "stderr": str(e)
            })

        print()

    return results


def generate_comprehensive_report(results):
    """Generate a comprehensive test report."""

    print("=" * 80)
    print("ADMIN CONVERSATION ANALYTICS - TEST EXECUTION SUMMARY")
    print("=" * 80)
    print()

    # Summary statistics
    total = results["total_tests"]
    passed = results["passed"]
    failed = results["failed"]
    skipped = results["skipped"]

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()

    # Detailed results
    print("DETAILED TEST RESULTS:")
    print("-" * 80)

    for detail in results["details"]:
        status_symbol = "✓" if detail["status"] == "PASSED" else "✗"
        print(f"{status_symbol} {detail['name']}: {detail['status']}")

    print()
    print("FEATURE VERIFICATION STATUS:")
    print("-" * 80)

    # Analyze which features were tested
    features_tested = [
        "Admin Dashboard Navigation",
        "Conversation Analytics Section Display",
        "Metrics Data Display",
        "Most Popular Service Display",
        "Data Consistency Validation",
        "Responsive Design",
        "Loading States",
        "API Integration",
        "UI Interactions",
        "Complete Feature Verification"
    ]

    for i, feature in enumerate(features_tested):
        if i < len(results["details"]):
            status = results["details"][i]["status"]
            status_symbol = "✓" if status == "PASSED" else "✗"
            print(f"{status_symbol} {feature}: {status}")

    print()
    print("RECOMMENDATIONS:")
    print("-" * 80)

    if failed == 0:
        print("🎉 All tests passed! The admin conversation analytics feature is working correctly.")
        print()
        print("✅ Key features verified:")
        print("   - Admin dashboard loads successfully")
        print("   - Conversation analytics section displays properly")
        print("   - All required metrics are shown (sessions, completion rate, conversion rates)")
        print("   - Most popular service is displayed when available")
        print("   - Data consistency is maintained")
        print("   - Responsive design works across viewports")
        print("   - Loading states and API integration work")
        print("   - UI interactions are functional")
        print("   - Complete feature verification passed")
    else:
        print(f"⚠️ {failed} test(s) failed. Review the issues below:")
        print()

        failed_tests = [d for d in results["details"] if d["status"] != "PASSED"]
        for test in failed_tests:
            print(f"❌ {test['name']}:")
            if test["stderr"]:
                print(f"   Error: {test['stderr'][:300]}...")
            print()

        print("🔧 Suggested fixes:")
        print("   - Check if backend API is running on localhost:8000")
        print("   - Verify frontend is running on localhost:5173")
        print("   - Ensure database has test data for analytics")
        print("   - Check browser automation dependencies (Playwright)")
        print("   - Verify admin authentication is working")
        print("   - Ensure conversation data exists in the system")

    print()
    print("TECHNICAL DETAILS:")
    print("-" * 80)
    print("• Test Framework: Playwright + Pytest")
    print("• Browser: Chromium (headless)")
    print("• Viewport: 1280x720 (responsive testing included)")
    print("• Timeout: 3 minutes per test")
    print("• Test Environment: Local development")
    print("• Test Type: End-to-End (E2E)")
    print()
    print("ANALYTICS METRICS TESTED:")
    print("-" * 80)
    print("• Total sessions count")
    print("• Completion rate")
    print("• PRD conversion rate")
    print("• Booking conversion rate")
    print("• Average session duration")
    print("• Average lead score")
    print("• Most popular service (when available)")
    print("• System health status")
    print("• Expert performance metrics")

    print()
    print("API ENDPOINTS TESTED:")
    print("-" * 80)
    print("• GET /admin - Admin dashboard page")
    print("• GET /api/v1/admin/analytics - System analytics")
    print("• GET /api/v1/admin/analytics/conversations - Conversation analytics")
    print("• GET /api/v1/admin/experts - Expert management data")

    # Save detailed report to file
    report_file = "admin_analytics_test_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📄 Detailed report saved to: {report_file}")
    print()
    print("=" * 80)


def main():
    """Main test execution function."""

    start_time = time.time()

    try:
        # Run the test suite
        results = run_analytics_test_suite()

        # Generate report
        generate_comprehensive_report(results)

        # Exit with appropriate code
        if results["failed"] == 0:
            print("✅ Admin conversation analytics tests completed successfully!")
            sys.exit(0)
        else:
            print("❌ Admin conversation analytics tests completed with failures.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n💥 Unexpected error during test execution: {e}")
        sys.exit(1)

    finally:
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ Total execution time: {duration:.2f} seconds")


if __name__ == "__main__":
    main()
