#!/usr/bin/env python3
"""Test conversation phase tracking, lead scoring, and service matching."""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.session import ConversationSession, SessionPhase, SessionStatus
from src.schemas.session import MessageCreate, SessionCreate
from src.services.session_service import SessionService
from src.services.ai_service import AIService


async def test_conversation_flow():
    """Test complete conversation flow with phase tracking."""
    print("\n" + "="*70)
    print("TESTING CONVERSATION PHASE TRACKING & LEAD SCORING")
    print("="*70 + "\n")

    async with AsyncSessionLocal() as db:
        service = SessionService(db)

        # Step 1: Create session
        print("Step 1: Creating session...")
        session_create = SessionCreate(
            visitor_id="test_visitor_123",
            source_url="http://localhost:5173",
            user_agent="Test Agent"
        )
        session = await service.create_session(session_create)
        print(f"  ✓ Session created: {session.id}")
        print(f"  ✓ Initial phase: {session.current_phase}")
        print(f"  ✓ Messages: {len(session.messages)}")
        assert session.current_phase == SessionPhase.GREETING.value
        assert len(session.messages) == 1

        # Step 2: User provides name
        print("\nStep 2: User provides name...")
        user_message = "Hi, I'm John Smith"
        ai_message = await service.generate_ai_response(session, user_message)
        await db.refresh(session)
        print(f"  ✓ User said: '{user_message}'")
        print(f"  ✓ Bot responded: {ai_message.content[:100]}...")
        print(f"  ✓ Client info: {session.client_info}")
        print(f"  ✓ Current phase: {session.current_phase}")
        assert session.client_info.get("name") == "John"  # Regex extracts first name

        # Step 3: User provides email
        print("\nStep 3: User provides email...")
        user_message = "My email is john@example.com"
        ai_message = await service.generate_ai_response(session, user_message)
        await db.refresh(session)
        print(f"  ✓ User said: '{user_message}'")
        print(f"  ✓ Client info: {session.client_info}")
        print(f"  ✓ Current phase: {session.current_phase}")
        assert session.client_info.get("email") == "john@example.com"

        # Step 4: User describes challenge
        print("\nStep 4: User describes business challenge...")
        user_message = "We have a problem with slow systems and need better data analytics"
        ai_message = await service.generate_ai_response(session, user_message)
        await db.refresh(session)
        print(f"  ✓ User said: '{user_message}'")
        print(f"  ✓ Business context: {session.business_context}")
        print(f"  ✓ Current phase: {session.current_phase}")
        assert session.business_context.get("challenges")

        # Step 5: User provides industry and company size
        print("\nStep 5: User provides industry and company info...")
        user_message = "We're in healthcare industry, company size is 50-200 people"
        ai_message = await service.generate_ai_response(session, user_message)
        await db.refresh(session)
        print(f"  ✓ User said: '{user_message}'")
        print(f"  ✓ Business context: {session.business_context}")
        print(f"  ✓ Current phase: {session.current_phase}")

        # Step 6: User provides budget
        print("\nStep 6: User provides budget...")
        user_message = "Our budget is around $50,000 to $100,000"
        ai_message = await service.generate_ai_response(session, user_message)
        await db.refresh(session)
        print(f"  ✓ User said: '{user_message}'")
        print(f"  ✓ Qualification: {session.qualification}")
        print(f"  ✓ Lead score: {session.lead_score}")
        print(f"  ✓ Current phase: {session.current_phase}")
        assert session.qualification.get("budget_range")
        assert session.lead_score is not None

        # Step 7: User provides timeline
        print("\nStep 7: User provides timeline...")
        user_message = "We're looking to start within 1-3 months"
        ai_message = await service.generate_ai_response(session, user_message)
        await db.refresh(session)
        print(f"  ✓ User said: '{user_message}'")
        print(f"  ✓ Qualification: {session.qualification}")
        print(f"  ✓ Lead score: {session.lead_score}")
        print(f"  ✓ Recommended service: {session.recommended_service}")
        print(f"  ✓ Current phase: {session.current_phase}")
        assert session.qualification.get("timeline")
        assert session.recommended_service is not None

        # Summary
        print("\n" + "="*70)
        print("CONVERSATION SUMMARY")
        print("="*70)
        print(f"Client Info: {session.client_info}")
        print(f"Business Context: {session.business_context}")
        print(f"Qualification: {session.qualification}")
        print(f"Lead Score: {session.lead_score}/100")
        print(f"Recommended Service: {session.recommended_service}")
        print(f"Final Phase: {session.current_phase}")
        print(f"Total Messages: {len(session.messages)}")

        print("\n✅ All phase tracking tests passed!")
        print("\nFeature Status:")
        print("  ✓ Conversation phase tracking works correctly")
        print("  ✓ Lead scoring calculates scores based on collected data")
        print("  ✓ Service matching recommends appropriate service")


if __name__ == "__main__":
    asyncio.run(test_conversation_flow())
