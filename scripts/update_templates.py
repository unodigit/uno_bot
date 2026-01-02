#!/usr/bin/env python3
"""Script to update welcome message templates in the database."""

import sqlite3
import uuid
import json

def update_templates():
    # Connect to the database
    conn = sqlite3.connect('unobot.db')
    cursor = conn.cursor()

    # First, clean up all existing templates to start fresh
    cursor.execute("DELETE FROM welcome_message_templates")
    conn.commit()

    # Create a proper default template that asks for the user's name
    default_template_id = str(uuid.uuid4())
    default_content = "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nI can help you explore our services, understand your needs, and connect you with the right expert.\n\nTo get started, what's your name?"

    cursor.execute("""
        INSERT INTO welcome_message_templates
        (id, name, content, description, target_industry, use_count, is_default, is_active, config, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        default_template_id,
        "Default Welcome Message",
        default_content,
        "Default welcome message for all users",
        "General",
        0,
        True,  # is_default
        True,  # is_active
        json.dumps({})  # config
    ))

    # Create a healthcare-specific template
    healthcare_template_id = str(uuid.uuid4())
    healthcare_content = "🎉 Welcome! I'm UnoBot, your AI healthcare consultant.\n\nI can help with patient data systems, HIPAA compliance, clinical workflows, and more.\n\nTo get started, what's your name?"

    cursor.execute("""
        INSERT INTO welcome_message_templates
        (id, name, content, description, target_industry, use_count, is_default, is_active, config, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        healthcare_template_id,
        "Healthcare Welcome Message",
        healthcare_content,
        "Welcome message for healthcare industry clients",
        "Healthcare",
        0,
        False,  # is_default
        True,   # is_active
        json.dumps({})  # config
    ))

    conn.commit()
    conn.close()

    print("Database updated successfully!")
    print(f"\nDefault template ID: {default_template_id}")
    print(f"Default content: {default_content[:80]}...")
    print(f"\nHealthcare template ID: {healthcare_template_id}")
    print(f"Healthcare content: {healthcare_content[:80]}...")

if __name__ == "__main__":
    update_templates()
