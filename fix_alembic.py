#!/usr/bin/env python3
"""Fix alembic version table to match current schema."""

import sqlite3
from pathlib import Path

def fix_alembic_version():
    """Fix the alembic version to match the current database state."""
    db_path = Path("unobot.db")

    if not db_path.exists():
        print("Database file not found!")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check current alembic version
        cursor.execute("SELECT version_num FROM alembic_version;")
        current_version = cursor.fetchone()
        print(f"Current alembic version: {current_version}")

        # Get the latest migration file
        latest_migration = "002_add_test_column"
        print(f"Expected latest migration: {latest_migration}")

        # Update the version
        cursor.execute("DELETE FROM alembic_version;")
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('002_add_test_column');")
        conn.commit()
        print("Alembic version updated successfully!")

    except Exception as e:
        print(f"Error fixing alembic version: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_alembic_version()