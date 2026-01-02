#!/usr/bin/env python3
"""
Session Resume E2E Test Runner

This script runs the comprehensive session resume via email link tests
and generates a detailed test report.
"""

import json
import subprocess
import sys
import time


def run_test_suite():
    """Run the session resume test suite and capture results."""

    print("=" * 80)
    print("UNOBOT SESSION RESUME VIA EMAIL LINK - E2E TEST SUITE")
    print("=" * 80)
    print()

    # Test suite configuration
    test_file = "tests/e2e/test_session_resume_email.py"
    test_patterns = [
        "test_session_resume_via_email_link",
        "test_session_resume_preserves_conversation_history",
        "test_session_resume_preserves_session_context",
        "test_session_resume_with_empty_conversation",
        "test_session_resume_url_generation",
        "test_session_resume_multiple_times",
        "test_session_resume_chat_widget_behavior",
        "test_session_resume_url_parameter_handling",
        "test_session_resume_without_parameter"
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
                timeout=300  # 5 minute timeout per test
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
                "stderr": "Test timed out after 5 minutes"
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


def generate_report(results):
    """Generate a comprehensive test report."""

    print("=" * 80)
    print("TEST EXECUTION SUMMARY")
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
    print("DETAILED RESULTS:")
    print("-" * 80)

    for detail in results["details"]:
        status_symbol = "✓" if detail["status"] == "PASSED" else "✗"
        print(f"{status_symbol} {detail['name']}: {detail['status']}")

    print()
    print("RECOMMENDATIONS:")
    print("-" * 80)

    if failed == 0:
        print("🎉 All tests passed! The session resume functionality is working correctly.")
        print()
        print("✅ Key features verified:")
        print("   - Session can be resumed via email links")
        print("   - Conversation history is preserved")
        print("   - Session context (phase, client info) is maintained")
        print("   - Multiple resume sessions work correctly")
        print("   - Chat widget behavior is correct after resume")
        print("   - URL generation works properly")
    else:
        print(f"⚠️ {failed} test(s) failed. Review the issues below:")
        print()

        failed_tests = [d for d in results["details"] if d["status"] != "PASSED"]
        for test in failed_tests:
            print(f"❌ {test['name']}:")
            if test["stderr"]:
                print(f"   Error: {test['stderr'][:200]}...")
            print()

        print("🔧 Suggested fixes:")
        print("   - Check if backend API is running on localhost:8000")
        print("   - Verify frontend is running on localhost:5173")
        print("   - Ensure database migrations are applied")
        print("   - Check browser automation dependencies")

    print()
    print("TECHNICAL DETAILS:")
    print("-" * 80)
    print("• Test Framework: Playwright + Pytest")
    print("• Browser: Chromium (headless)")
    print("• Viewport: 1280x720")
    print("• Timeout: 5 minutes per test")
    print("• Test Environment: Local development")
    print()

    # Save detailed report to file
    report_file = "session_resume_test_report.json"
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
        results = run_test_suite()

        # Generate report
        generate_report(results)

        # Exit with appropriate code
        if results["failed"] == 0:
            print("✅ Test execution completed successfully!")
            sys.exit(0)
        else:
            print("❌ Test execution completed with failures.")
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
