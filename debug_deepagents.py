#!/usr/bin/env python3
"""
Debug the DeepAgents service directly
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.core.config import settings
from src.services.deepagents_service import DeepAgentsService

async def test_deepagents():
    print("🔍 Testing DeepAgents service directly...")

    # Create database connection
    engine = create_async_engine(settings.database_url)
    async with AsyncSession(engine) as session:
        try:
            # Initialize DeepAgents service
            agent_service = DeepAgentsService(session)

            if not agent_service.agent:
                print("❌ DeepAgents not initialized - no agent available")
                return False

            print("✅ DeepAgents service initialized")

            # Test agent invocation
            test_input = {
                "user_message": "Hello, I need help with a project",
                "session_context": {
                    "client_info": {},
                    "business_context": {},
                    "current_phase": "greeting"
                },
                "conversation_history": [],
                "current_time": "2026-01-03T01:00:00Z"
            }

            print("🔄 Invoking agent...")
            response = await agent_service.agent.ainvoke(test_input)
            print(f"✅ Agent response: {response}")

            # Check if response has content
            content = response.get("content", "")
            if content:
                print(f"✅ Agent generated response: {content[:100]}...")
            else:
                print("❌ Agent returned empty content")

            return True

        except Exception as e:
            print(f"❌ DeepAgents test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    asyncio.run(test_deepagents())