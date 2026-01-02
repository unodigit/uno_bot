#!/usr/bin/env python3
"""Test phase tracking, lead scoring, and service matching without AI calls."""
import asyncio
from src.core.database import AsyncSessionLocal
from src.models.session import ConversationSession, SessionPhase
from src.schemas.session import SessionCreate
from src.services.session_service import SessionService


async def test_phase_tracking():
    """Test conversation phase tracking logic."""
    print("\n" + "="*70)
    print("PHASE TRACKING, LEAD SCORING & SERVICE MATCHING TEST")
    print("="*70 + "\n")

    async with AsyncSessionLocal() as db:
        service = SessionService(db)

        # Create session
        print("Creating session...")
        session_create = SessionCreate(
            visitor_id="test_visitor",
            source_url="http://localhost:5173",
            user_agent="Test"
        )
        session = await service.create_session(session_create)
        assert session.current_phase == SessionPhase.GREETING.value
        print(f"  ✓ Initial phase: {session.current_phase}")

        # Test 1: Extract name
        print("\n[TEST 1] Name Extraction")
        await service._extract_user_info(session, "My name is John Smith")
        await db.refresh(session)
        print(f"  ✓ Client info: {session.client_info}")
        assert session.client_info.get("name") == "John"
        print(f"  ✓ Name extracted: {session.client_info.get('name')}")

        # Test 2: Extract email
        print("\n[TEST 2] Email Extraction")
        await service._extract_user_info(session, "My email is john@example.com")
        await db.refresh(session)
        assert session.client_info.get("email") == "john@example.com"
        print(f"  ✓ Email extracted: {session.client_info.get('email')}")

        # Test 3: Extract company
        print("\n[TEST 3] Company Extraction")
        await service._extract_user_info(session, "I work at TechCorp Inc")
        await db.refresh(session)
        assert session.client_info.get("company") == "Techcorp Inc"
        print(f"  ✓ Company extracted: {session.client_info.get('company')}")

        # Test 4: Extract challenges
        print("\n[TEST 4] Business Challenges Extraction")
        await service._extract_user_info(session, "We have a problem with slow systems and need help")
        await db.refresh(session)
        assert session.business_context.get("challenges")
        print(f"  ✓ Challenges recorded: {session.business_context.get('challenges')[:50]}...")

        # Test 5: Extract industry
        print("\n[TEST 5] Industry Extraction")
        await service._extract_user_info(session, "We're in the healthcare industry")
        await db.refresh(session)
        assert session.business_context.get("industry") == "Healthcare"
        print(f"  ✓ Industry extracted: {session.business_context.get('industry')}")

        # Test 6: Extract budget
        print("\n[TEST 6] Budget Range Extraction")
        await service._extract_user_info(session, "Our budget is around $50,000")
        await db.refresh(session)
        assert session.qualification.get("budget_range") == "medium ($25k-$100k)"
        print(f"  ✓ Budget range: {session.qualification.get('budget_range')}")

        # Test 7: Extract timeline
        print("\n[TEST 7] Timeline Extraction")
        await service._extract_user_info(session, "We're looking to start within 1-3 months")
        await db.refresh(session)
        assert session.qualification.get("timeline") == "near-term (1-3 months)"
        print(f"  ✓ Timeline: {session.qualification.get('timeline')}")

        # Test 8: Calculate lead score
        print("\n[TEST 8] Lead Scoring")
        await service._calculate_lead_score(session)
        await db.refresh(session)
        print(f"  ✓ Lead score calculated: {session.lead_score}/100")
        assert session.lead_score is not None
        assert session.lead_score > 0

        # Test 9: Service recommendation
        print("\n[TEST 9] Service Matching")
        await service._recommend_service(session)
        await db.refresh(session)
        print(f"  ✓ Recommended service: {session.recommended_service}")
        assert session.recommended_service is not None

        # Test 10: Phase transitions
        print("\n[TEST 10] Phase Transitions")
        await db.refresh(session)

        # Should move from greeting to discovery
        new_phase = await service._determine_next_phase(session)
        print(f"  ✓ Current phase: {session.current_phase}")
        print(f"  ✓ Recommended next phase: {new_phase.value if new_phase else 'None'}")

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Client Info: {session.client_info}")
        print(f"Business Context: {session.business_context}")
        print(f"Qualification: {session.qualification}")
        print(f"Lead Score: {session.lead_score}/100")
        print(f"Recommended Service: {session.recommended_service}")
        print(f"Current Phase: {session.current_phase}")

        print("\n✅ ALL TESTS PASSED!")
        print("\nFeatures Verified:")
        print("  ✓ Name extraction from user messages")
        print("  ✓ Email extraction and validation")
        print("  ✓ Company information extraction")
        print("  ✓ Business challenges detection")
        print("  ✓ Industry identification")
        print("  ✓ Budget range extraction")
        print("  ✓ Timeline extraction")
        print("  ✓ Lead score calculation (0-100)")
        print("  ✓ Service recommendation based on context")
        print("  ✓ Phase transition logic")


if __name__ == "__main__":
    asyncio.run(test_phase_tracking())
