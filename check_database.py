#!/usr/bin/env python3
"""
Check database schema and fix migration issues.
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import List, Tuple

async def check_database_schema():
    """Check the current database schema."""
    db_path = "/media/DATA/projects/autonomous-coding-uno-bot/unobot/unobot.db"

    # Check if database exists
    if not Path(db_path).exists():
        print("Database file not found!")
        return

    # Connect and check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")

        # Check prd_documents table schema
        if "prd_documents" in tables:
            cursor.execute("PRAGMA table_info(prd_documents);")
            columns = cursor.fetchall()
            print(f"\nPRD Documents table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")

            # Check for missing columns
            column_names = [col[1] for col in columns]
            required_columns = [
                'id', 'session_id', 'version', 'content_markdown',
                'conversation_summary', 'client_company', 'client_name',
                'recommended_service', 'matched_expert_id', 'storage_url',
                'download_count', 'created_at', 'expires_at'
            ]

            missing_columns = [col for col in required_columns if col not in column_names]
            if missing_columns:
                print(f"\nMissing columns: {missing_columns}")

                # Try to add missing columns
                for column in missing_columns:
                    if column == 'conversation_summary':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'download_count':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} INTEGER DEFAULT 0;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'expires_at':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'client_company':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'client_name':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'recommended_service':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'matched_expert_id':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    elif column == 'storage_url':
                        try:
                            cursor.execute(f"ALTER TABLE prd_documents ADD COLUMN {column} TEXT;")
                            print(f"  Added column: {column}")
                        except Exception as e:
                            print(f"  Failed to add column {column}: {e}")
                    # Skip id, session_id, version, content_markdown, created_at as they should exist
            else:
                print("\nAll required columns present!")

        # Check other tables
        for table in tables:
            if table != 'prd_documents':
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                print(f"\n{table} table columns: {[col[1] for col in columns]}")

        conn.commit()
        print("\nDatabase schema check complete!")

    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(check_database_schema())