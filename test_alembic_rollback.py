"""
Test Alembic Migration Rollback

This test verifies that Alembic migrations can be:
1. Applied (upgrade)
2. Rolled back (downgrade)
3. Re-applied after rollback

The test creates a temporary database, applies migrations, and tests rollback.
"""

import asyncio
import sqlite3
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from alembic import command
from alembic.config import Config

# Test configuration
TEST_DB_PATH = "test_alembic_rollback.db"
ALEMBIC_INI_PATH = "alembic.ini"


def clean_test_db():
    """Remove test database if it exists."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"✅ Cleaned up test database: {TEST_DB_PATH}")


def check_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def run_alembic_command(alembic_cfg, cmd, **kwargs):
    """Run an Alembic command with error handling."""
    try:
        if cmd == 'upgrade':
            command.upgrade(alembic_cfg, **kwargs)
        elif cmd == 'downgrade':
            command.downgrade(alembic_cfg, **kwargs)
        elif cmd == 'current':
            command.current(alembic_cfg, **kwargs)
        elif cmd == 'history':
            command.history(alembic_cfg, **kwargs)
        return True, None
    except Exception as e:
        return False, str(e)


def test_alembic_rollback():
    """Test Alembic migration and rollback functionality."""

    print("\n" + "="*60)
    print("Alembic Migration Rollback Test")
    print("="*60 + "\n")

    test_results = []

    # Test 1: Setup and initial migration
    print("Test 1: Initial Migration")
    try:
        clean_test_db()

        # Create Alembic config
        alembic_cfg = Config(ALEMBIC_INI_PATH)

        # Set test database URL
        test_db_url = f"sqlite:///{TEST_DB_PATH}"
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # Run initial migration
        success, error = run_alembic_command(alembic_cfg, 'upgrade', revision='head')

        if success:
            print("✅ PASS: Initial migration applied successfully")

            # Verify table was created
            engine = create_engine(test_db_url)
            if check_table_exists(engine, 'alembic_test'):
                print("   Verified: Table 'alembic_test' exists")

                # Check columns
                if check_column_exists(engine, 'alembic_test', 'name'):
                    print("   Verified: Column 'name' exists")
                    test_results.append(("Initial migration", True))
                else:
                    print("❌ FAIL: Column 'name' not found")
                    test_results.append(("Initial migration", False))
            else:
                print("❌ FAIL: Table 'alembic_test' not created")
                test_results.append(("Initial migration", False))

            engine.dispose()
        else:
            print(f"❌ FAIL: Migration failed: {error}")
            test_results.append(("Initial migration", False))

    except Exception as e:
        print(f"❌ FAIL: Exception during initial migration: {e}")
        test_results.append(("Initial migration", False))

    print()

    # Test 2: Second migration
    print("Test 2: Second Migration (Add Column)")
    try:
        alembic_cfg = Config(ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # Should already be at head, but let's verify
        success, error = run_alembic_command(alembic_cfg, 'upgrade', revision='head')

        if success:
            print("✅ PASS: Second migration applied successfully")

            # Verify column was added
            engine = create_engine(test_db_url)
            if check_column_exists(engine, 'alembic_test', 'description'):
                print("   Verified: Column 'description' exists")
                test_results.append(("Second migration", True))
            else:
                print("❌ FAIL: Column 'description' not found")
                test_results.append(("Second migration", False))

            engine.dispose()
        else:
            print(f"❌ FAIL: Second migration failed: {error}")
            test_results.append(("Second migration", False))

    except Exception as e:
        print(f"❌ FAIL: Exception during second migration: {e}")
        test_results.append(("Second migration", False))

    print()

    # Test 3: Rollback one migration
    print("Test 3: Rollback One Migration")
    try:
        alembic_cfg = Config(ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # Rollback to version 001
        success, error = run_alembic_command(alembic_cfg, 'downgrade', revision='001')

        if success:
            print("✅ PASS: Rollback to version 001 successful")

            # Verify column was removed
            engine = create_engine(test_db_url)
            if not check_column_exists(engine, 'alembic_test', 'description'):
                print("   Verified: Column 'description' removed")
                test_results.append(("Rollback one migration", True))
            else:
                print("❌ FAIL: Column 'description' still exists")
                test_results.append(("Rollback one migration", False))

            engine.dispose()
        else:
            print(f"❌ FAIL: Rollback failed: {error}")
            test_results.append(("Rollback one migration", False))

    except Exception as e:
        print(f"❌ FAIL: Exception during rollback: {e}")
        test_results.append(("Rollback one migration", False))

    print()

    # Test 4: Rollback to base
    print("Test 4: Rollback to Base (Remove All Migrations)")
    try:
        alembic_cfg = Config(ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # Rollback to base
        success, error = run_alembic_command(alembic_cfg, 'downgrade', revision='base')

        if success:
            print("✅ PASS: Rollback to base successful")

            # Verify table was removed
            engine = create_engine(test_db_url)
            if not check_table_exists(engine, 'alembic_test'):
                print("   Verified: Table 'alembic_test' removed")
                test_results.append(("Rollback to base", True))
            else:
                print("❌ FAIL: Table 'alembic_test' still exists")
                test_results.append(("Rollback to base", False))

            engine.dispose()
        else:
            print(f"❌ FAIL: Rollback to base failed: {error}")
            test_results.append(("Rollback to base", False))

    except Exception as e:
        print(f"❌ FAIL: Exception during rollback to base: {e}")
        test_results.append(("Rollback to base", False))

    print()

    # Test 5: Re-apply migrations after rollback
    print("Test 5: Re-apply Migrations After Rollback")
    try:
        alembic_cfg = Config(ALEMBIC_INI_PATH)
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # Upgrade to head again
        success, error = run_alembic_command(alembic_cfg, 'upgrade', revision='head')

        if success:
            print("✅ PASS: Re-applied migrations successfully")

            # Verify everything is back
            engine = create_engine(test_db_url)
            table_exists = check_table_exists(engine, 'alembic_test')
            has_name = check_column_exists(engine, 'alembic_test', 'name')
            has_description = check_column_exists(engine, 'alembic_test', 'description')

            if table_exists and has_name and has_description:
                print("   Verified: All migrations re-applied correctly")
                test_results.append(("Re-apply migrations", True))
            else:
                print(f"❌ FAIL: Missing objects (table: {table_exists}, name: {has_name}, desc: {has_description})")
                test_results.append(("Re-apply migrations", False))

            engine.dispose()
        else:
            print(f"❌ FAIL: Re-apply migrations failed: {error}")
            test_results.append(("Re-apply migrations", False))

    except Exception as e:
        print(f"❌ FAIL: Exception during re-apply: {e}")
        test_results.append(("Re-apply migrations", False))

    print()

    # Clean up
    print("Cleanup")
    try:
        clean_test_db()
        print("✅ Test database cleaned up")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up test database: {e}")

    # Print summary
    print("\n" + "="*60)
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
    """Main test runner."""
    try:
        results = test_alembic_rollback()

        # Save results to JSON
        output_file = Path("test_results_alembic_rollback.json")
        import json
        with open(output_file, 'w') as f:
            json.dump([{"test": name, "passed": result} for name, result in results], f, indent=2)

        print(f"Test results saved to: {output_file}\n")

        # Return exit code
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
