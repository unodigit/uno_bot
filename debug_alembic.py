#!/usr/bin/env python3
"""Debug script to see what's happening with Alembic migrations."""

import sqlite3
import os
from sqlalchemy import create_engine, inspect, text
from alembic import command
from alembic.config import Config

TEST_DB = "debug_test.db"

# Clean up
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

# Create config
test_db_url = f"sqlite:///{TEST_DB}"
alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

print("Running upgrade to head...")
command.upgrade(alembic_cfg, 'head')

print("\nChecking what was created...")
engine = create_engine(test_db_url)
inspector = inspect(engine)

print(f"\nTables in database: {inspector.get_table_names()}")

# Check alembic version
with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    version = result.scalar()
    print(f"Current Alembic version: {version}")

print(f"\nColumns in test_table:")
for col in inspector.get_columns('test_table'):
    print(f"  - {col['name']}: {col['type']}")

engine.dispose()

# Clean up
os.remove(TEST_DB)
print(f"\nCleaned up {TEST_DB}")
