#!/usr/bin/env python3
"""Reset alembic version to match the actual database schema."""

import sqlite3
from pathlib import Path

def reset_alembic_version():
    """Reset alembic version to match current database state."""
    db_path = Path("unobot.db")

    if not db_path.exists():
        print("Database file not found!")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Get a list of all tables to understand the current schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Current tables: {tables}")

        # Since we have the full schema already created, let's mark it as up to date
        # by removing the alembic_version table entirely and letting alembic know
        # the current state matches the latest migration

        # First, remove the old version
        cursor.execute("DELETE FROM alembic_version;")

        # Since we have a complex schema already, we'll create a new migration
        # that represents the current state. For now, let's just mark it as current.
        # The key is to make alembic recognize the current state.

        # Let's check what the latest migration file is
        latest_revision = "002"  # Based on the files we saw
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?);", (latest_revision,))
        conn.commit()
        print(f"Alembic version reset to: {latest_revision}")

    except Exception as e:
        print(f"Error resetting alembic version: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_alembic_version()