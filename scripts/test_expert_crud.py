#!/usr/bin/env python3
"""Test script for Expert CRUD operations."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx


async def test_expert_crud():
    """Test Expert CRUD operations."""
    base_url = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        # Step 1: Create an expert
        print("=" * 60)
        print("Step 1: Creating new expert")
        print("=" * 60)

        expert_data = {
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
                "timezone": "America/New_York"
            }
        }

        response = await client.post(f"{base_url}/api/v1/experts", json=expert_data)
        print(f"Status: {response.status_code}")

        if response.status_code != 201:
            print(f"Error: {response.text}")
            return False

        expert = response.json()
        expert_id = expert["id"]
        print(f"Expert ID: {expert_id}")
        print(f"Name: {expert['name']}")
        print(f"Role: {expert['role']}")
        print(f"Specialties: {expert['specialties']}")

        # Step 2: Read the expert
        print("\n" + "=" * 60)
        print("Step 2: Reading expert")
        print("=" * 60)

        response = await client.get(f"{base_url}/api/v1/experts/{expert_id}")
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        expert_read = response.json()
        print(f"Retrieved: {expert_read['name']} - {expert_read['role']}")

        # Step 3: Update the expert
        print("\n" + "=" * 60)
        print("Step 3: Updating expert")
        print("=" * 60)

        update_data = {
            "bio": "Updated bio: Leading AI strategist with expertise in healthcare and finance.",
            "specialties": ["AI/ML", "Data Strategy", "Healthcare AI", "FinTech"]
        }

        response = await client.put(f"{base_url}/api/v1/experts/{expert_id}", json=update_data)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        updated_expert = response.json()
        print(f"Updated bio: {updated_expert['bio'][:50]}...")
        print(f"Updated specialties: {updated_expert['specialties']}")

        # Step 4: List all experts
        print("\n" + "=" * 60)
        print("Step 4: Listing all experts")
        print("=" * 60)

        response = await client.get(f"{base_url}/api/v1/experts")
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        experts = response.json()
        print(f"Total experts: {len(experts)}")
        for exp in experts:
            print(f"  - {exp['name']} ({exp['role']})")

        # Step 5: Delete the expert
        print("\n" + "=" * 60)
        print("Step 5: Deleting expert")
        print("=" * 60)

        response = await client.delete(f"{base_url}/api/v1/experts/{expert_id}")
        print(f"Status: {response.status_code}")

        if response.status_code != 204:
            print(f"Error: {response.text}")
            return False

        # Verify deletion
        response = await client.get(f"{base_url}/api/v1/experts/{expert_id}")
        if response.status_code == 404:
            print("✓ Expert successfully deleted")
        else:
            print("✗ Expert still exists after deletion")
            return False

        print("\n" + "=" * 60)
        print("✓ All Expert CRUD tests passed!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_expert_crud())
    sys.exit(0 if success else 1)
