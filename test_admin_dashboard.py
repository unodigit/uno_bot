#!/usr/bin/env python3
"""
Test admin dashboard features
"""

import requests
import uuid
import json

BASE_URL = "http://localhost:8000"

def test_admin_dashboard():
    print("🧪 Testing Admin Dashboard Features")
    print("=" * 50)

    try:
        # Test 1: Create admin token
        print("1. Testing admin authentication...")
        admin_response = requests.post(f"{BASE_URL}/api/v1/admin/auth/token", json={
            "username": "admin",
            "password": "admin123"
        })

        print(f"   Admin token creation: {admin_response.status_code}")

        if admin_response.status_code == 200:
            token_data = admin_response.json()
            admin_token = token_data.get('access_token', '')
            print(f"   ✅ Admin token created: {admin_token[:20]}...")
        else:
            print(f"   ⚠️  Admin auth not configured, using fallback")
            admin_token = None

        # Test 2: List experts (admin endpoint)
        print("2. Testing expert management...")
        headers = {}
        if admin_token:
            headers["X-Admin-Token"] = admin_token

        experts_response = requests.get(f"{BASE_URL}/api/v1/admin/experts", headers=headers)

        print(f"   Experts endpoint: {experts_response.status_code}")

        if experts_response.status_code == 200:
            experts = experts_response.json()
            print(f"   ✅ Experts listed: {len(experts)}")
            if experts:
                expert = experts[0]
                print(f"   First expert: {expert.get('name', 'N/A')} - {expert.get('role', 'N/A')}")
        else:
            print(f"   ❌ Experts endpoint failed: {experts_response.text}")

        # Test 3: Get analytics
        print("3. Testing analytics dashboard...")
        analytics_response = requests.get(f"{BASE_URL}/api/v1/admin/analytics", headers=headers)

        print(f"   Analytics endpoint: {analytics_response.status_code}")

        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            print(f"   ✅ Analytics available: {len(analytics)} metrics")
            for key, value in list(analytics.items())[:5]:
                print(f"     {key}: {value}")
        else:
            print(f"   ❌ Analytics endpoint failed: {analytics_response.text}")

        # Test 4: Get conversation analytics
        print("4. Testing conversation analytics...")
        conv_analytics_response = requests.get(f"{BASE_URL}/api/v1/admin/analytics/conversations", headers=headers)

        print(f"   Conversation analytics: {conv_analytics_response.status_code}")

        if conv_analytics_response.status_code == 200:
            conv_analytics = conv_analytics_response.json()
            print(f"   ✅ Conversation analytics available")
            for key, value in list(conv_analytics.items())[:5]:
                print(f"     {key}: {value}")
        else:
            print(f"   ❌ Conversation analytics failed: {conv_analytics_response.text}")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_admin_dashboard()