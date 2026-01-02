#!/usr/bin/env python3
"""
Test the session service's response generation
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.core.config import settings
from src.services.session_service import SessionService
from src.services.ai_service import AIService

async def test_session_service():
    print("🔍 Testing Session Service response generation...")

    # Create database connection
    engine = create_async_engine(settings.database_url)
    async with AsyncSession(engine) as session:
        try:
            # Initialize services
            session_service = SessionService(session)

            # Test the _generate_streaming_response method directly
            user_message = "Hello"
            conversation_history = []
            context = {
                "business_context": {},
                "client_info": {},
                "qualification": {},
                "current_phase": "greeting"
            }

            print("🔄 Testing _generate_streaming_response...")
            response = await session_service._generate_streaming_response(
                user_message, conversation_history, context
            )

            print(f"✅ Streaming response: '{response}'")
            print(f"Response length: {len(response)}")

            if response:
                print("✅ Session service response generation working!")
                return True
            else:
                print("❌ Session service returned empty response")
                return False

        except Exception as e:
            print(f"❌ Session service test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    asyncio.run(test_session_service())