#!/usr/bin/env python3
"""
Test the AI service directly to debug the empty response issue
"""

import asyncio
from src.services.ai_service import AIService

async def test_ai_service():
    print("🔍 Testing AI Service directly...")

    try:
        # Initialize AI service
        ai_service = AIService()
        print(f"✅ AI Service initialized - LLM: {ai_service.llm is not None}")

        # Test fallback response
        user_message = "Hello"
        context = {
            "client_info": {},
            "business_context": {},
            "qualification": {}
        }

        print("🔄 Testing fallback response...")
        response = await ai_service.generate_response(user_message, [], context)
        print(f"✅ Response: '{response}'")
        print(f"Response length: {len(response)}")

        # Test streaming response
        print("🔄 Testing streaming response...")
        try:
            streaming_response = ""
            async for chunk in ai_service.stream_response(user_message, [], context):
                streaming_response += chunk
                print(f"Chunk: '{chunk}'")

            print(f"✅ Streaming response: '{streaming_response}'")
            print(f"Streaming response length: {len(streaming_response)}")
        except Exception as e:
            print(f"❌ Streaming failed: {e}")

        return True

    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_ai_service())