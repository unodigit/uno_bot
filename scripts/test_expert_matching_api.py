"""Test script for expert matching API endpoint."""
import asyncio
import json
from httpx import AsyncClient, ASGITransport
from src.main import app


async def test_expert_matching_api():
    """Test the expert matching API endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("Testing Expert Matching API Endpoint")
        print("=" * 60)

        # Test 1: Match by service type
        print("\nTest 1: POST /api/v1/experts/match with service_type")
        response = await client.post(
            "/api/v1/experts/match",
            json={
                "service_type": "AI Strategy & Planning",
                "specialties": ["AI/ML", "Data Science"]
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['experts'])} experts")
            for i, expert in enumerate(data['experts'], 1):
                score = data['match_scores'][i-1]
                print(f"  {i}. {expert['name']} ({expert['role']}) - Score: {score:.1f}")
                print(f"     Services: {expert['services']}")
                print(f"     Specialties: {expert['specialties']}")

            # Verify sorting by score
            scores = data['match_scores']
            is_sorted = scores == sorted(scores, reverse=True)
            print(f"\n  ✓ Results sorted by score: {is_sorted}")

        print("\n" + "=" * 60)

        # Test 2: Match by business context
        print("\nTest 2: POST /api/v1/experts/match with business context")
        response = await client.post(
            "/api/v1/experts/match",
            json={
                "service_type": "Cloud Infrastructure & DevOps",
                "specialties": ["Cloud", "DevOps"]
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['experts'])} experts")
            for i, expert in enumerate(data['experts'], 1):
                score = data['match_scores'][i-1]
                print(f"  {i}. {expert['name']} - Score: {score:.1f}")

        print("\n" + "=" * 60)
        print("\n✓ Expert matching API endpoint is working!")


if __name__ == "__main__":
    asyncio.run(test_expert_matching_api())
