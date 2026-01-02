#!/usr/bin/env python3
"""Seed test experts for E2E testing."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx


async def seed_test_experts():
    """Create test experts for E2E testing."""
    base_url = "http://localhost:8001"

    # Test experts data
    experts_data = [
        {
            "name": "Dr. Sarah Chen",
            "email": "sarah.chen@unodigit.com",
            "role": "AI Strategy Lead",
            "bio": "Expert in machine learning and digital transformation with 15+ years experience.",
            "photo_url": "https://example.com/photos/sarah.jpg",
            "specialties": ["AI/ML", "Data Strategy", "Digital Transformation"],
            "services": ["AI Strategy & Planning", "Data Intelligence & Analytics"],
            "availability": {
                "business_hours_start": "09:00",
                "business_hours_end": "17:00",
                "timezone": "UTC"
            }
        },
        {
            "name": "Alex Rodriguez",
            "email": "alex.rodriguez@unodigit.com",
            "role": "Senior Software Architect",
            "bio": "Full-stack developer and cloud architect specializing in scalable web applications.",
            "photo_url": "https://example.com/photos/alex.jpg",
            "specialties": ["Full-Stack Development", "Cloud Architecture", "DevOps"],
            "services": ["Custom Software Development", "Cloud Migration & Strategy"],
            "availability": {
                "business_hours_start": "09:00",
                "business_hours_end": "17:00",
                "timezone": "UTC"
            }
        },
        {
            "name": "Emily Zhang",
            "email": "emily.zhang@unodigit.com",
            "role": "Data Intelligence Specialist",
            "bio": "Data scientist focused on business intelligence and advanced analytics solutions.",
            "photo_url": "https://example.com/photos/emily.jpg",
            "specialties": ["Business Intelligence", "Advanced Analytics", "Data Visualization"],
            "services": ["Data Intelligence & Analytics", "AI Strategy & Planning"],
            "availability": {
                "business_hours_start": "09:00",
                "business_hours_end": "17:00",
                "timezone": "UTC"
            }
        }
    ]

    async with httpx.AsyncClient() as client:
        print("Seeding test experts...")

        for i, expert_data in enumerate(experts_data, 1):
            print(f"\nCreating expert {i}/3: {expert_data['name']}")

            response = await client.post(f"{base_url}/api/v1/experts", json=expert_data)

            if response.status_code == 201:
                expert = response.json()
                print(f"✓ Created: {expert['name']} (ID: {expert['id']})")
            else:
                print(f"✗ Failed to create {expert_data['name']}: {response.text}")

        # List all experts
        print("\nListing all experts:")
        response = await client.get(f"{base_url}/api/v1/experts")
        if response.status_code == 200:
            experts = response.json()
            for expert in experts:
                print(f"  - {expert['name']} ({expert['role']})")
            print(f"\nTotal experts: {len(experts)}")
        else:
            print(f"Failed to list experts: {response.text}")


if __name__ == "__main__":
    asyncio.run(seed_test_experts())