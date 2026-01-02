"""
Simple Test for Alembic Migration Rollback
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect
from alembic import command
from alembic.config import Config

TEST_DB_PATH = "test_alembic_simple.db"
ALEMBIC_INI_PATH = "alembic.ini"


def clean_test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"✅ Cleaned up test database: {TEST_DB_PATH}")


def check_table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def test_rollback():
    print("\n" + "="*60)
    print("Alembic Migration Rollback Test")
    print("="*60 + "\n")

    test_results = []

    # Setup
    print("Setup: Creating test database and Alembic config")
    try:
        clean_test_db()
        test_db_url = f"sqlite:///{TEST_DB_PATH}"

        alembic_cfg = Config(ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        print("✅ Test database and config ready\n")
    except Exception as e:
        print(f"❌ FAIL: Setup failed: {e}")
        return []

    # Test 1: Apply migration
    print("Test 1: Apply Migration (Create Table)")
    try:
        command.upgrade(alembic_cfg, 'head')

        engine = create_engine(test_db_url)
        if check_table_exists(engine, 'test_table'):
            print("✅ PASS: Migration applied - test_table exists")
            test_results.append(("Apply migration", True))
        else:
            print("❌ FAIL: Migration applied but table not found")
            test_results.append(("Apply migration", False))
        engine.dispose()
    except Exception as e:
        print(f"❌ FAIL: Exception: {e}")
        test_results.append(("Apply migration", False))

    print()

    # Test 2: Rollback migration
    print("Test 2: Rollback Migration (Drop Table)")
    try:
        command.downgrade(alembic_cfg, 'd280d291ddfc')

        engine = create_engine(test_db_url)
        if not check_table_exists(engine, 'test_table'):
            print("✅ PASS: Rollback successful - test_table removed")
            test_results.append(("Rollback migration", True))
        else:
            print("❌ FAIL: Rollback executed but table still exists")
            test_results.append(("Rollback migration", False))
        engine.dispose()
    except Exception as e:
        print(f"❌ FAIL: Exception: {e}")
        test_results.append(("Rollback migration", False))

    print()

    # Test 3: Re-apply after rollback
    print("Test 3: Re-apply Migration After Rollback")
    try:
        command.upgrade(alembic_cfg, 'head')

        engine = create_engine(test_db_url)
        if check_table_exists(engine, 'test_table'):
            print("✅ PASS: Re-applied successfully")
            test_results.append(("Re-apply migration", True))
        else:
            print("❌ FAIL: Re-applied but table not found")
            test_results.append(("Re-apply migration", False))
        engine.dispose()
    except Exception as e:
        print(f"❌ FAIL: Exception: {e}")
        test_results.append(("Re-apply migration", False))

    print()

    # Test 4: Rollback to base
    print("Test 4: Rollback to Base")
    try:
        command.downgrade(alembic_cfg, 'base')

        engine = create_engine(test_db_url)
        if not check_table_exists(engine, 'test_table'):
            print("✅ PASS: Rollback to base successful")
            test_results.append(("Rollback to base", True))
        else:
            print("❌ FAIL: Table still exists after rollback to base")
            test_results.append(("Rollback to base", False))
        engine.dispose()
    except Exception as e:
        print(f"❌ FAIL: Exception: {e}")
        test_results.append(("Rollback to base", False))

    print()

    # Cleanup
    print("Cleanup")
    try:
        clean_test_db()
        print("✅ Test database cleaned up\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up: {e}\n")

    # Print summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    for name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*60 + "\n")

    return test_results


def main():
    try:
        results = test_rollback()

        # Save results
        output_file = Path("test_results_alembic_rollback.json")
        import json
        with open(output_file, 'w') as f:
            json.dump([{"test": name, "passed": result} for name, result in results], f, indent=2)

        print(f"Test results saved to: {output_file}\n")

        passed = sum(1 for _, result in results if result)
        total = len(results)
        if passed == total:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {total - passed} test(s) failed")
            return 1

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
