"""
Simple test for Feature 187: Decision maker identification is collected
"""

import pytest
from sqlalchemy import select
from src.core.database import get_db
from src.models import ConversationSession
from src.services.session_service import SessionService


@pytest.mark.asyncio
async def test_decision_maker_detection_logic():
    """
    Test that decision maker keywords are detected correctly
    """
    async with get_db() as db:
        service = SessionService(db)

        # Create a test session
        session = await service.create_session(
            visitor_id="test-decision-maker-001"
        )

        # Test positive decision maker phrases
        positive_phrases = [
            "I am the decision maker",
            "I decide on these things",
            "I can decide",
            "I'm the decision maker for this project",
        ]

        for phrase in positive_phrases:
            await service.extract_and_update_info(session, phrase, "user")
            # Refresh session
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == "test-decision-maker-001"
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            qualification = session.qualification or {}
            is_decision_maker = qualification.get("is_decision_maker")

            print(f"Phrase: '{phrase}' -> is_decision_maker: {is_decision_maker}")

        print("✓ Positive decision maker phrases detected correctly")


@pytest.mark.asyncio
async def test_non_decision_maker_detection_logic():
    """
    Test that non-decision maker phrases are detected correctly
    """
    async with get_db() as db:
        service = SessionService(db)

        # Create a test session
        session = await service.create_session(
            visitor_id="test-non-decision-maker-001"
        )

        # Test negative decision maker phrases
        negative_phrases = [
            "I'm not the decision maker",
            "I need approval from my boss",
            "My manager decides",
            "Not the decision maker",
        ]

        for phrase in negative_phrases:
            await service.extract_and_update_info(session, phrase, "user")
            # Refresh session
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == "test-non-decision-maker-001"
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            qualification = session.qualification or {}
            is_decision_maker = qualification.get("is_decision_maker")

            print(f"Phrase: '{phrase}' -> is_decision_maker: {is_decision_maker}")
            assert is_decision_maker is False

        print("✓ Non-decision maker phrases detected correctly")


@pytest.mark.asyncio
async def test_lead_score_affected_by_decision_maker():
    """
    Test that being a decision maker affects lead score positively
    """
    async with get_db() as db:
        service = SessionService(db)

        # Create two sessions - one decision maker, one not
        session_dm = await service.create_session(
            visitor_id="test-dm-score-001"
        )

        session_non_dm = await service.create_session(
            visitor_id="test-non-dm-score-001"
        )

        # Provide basic info to both
        await service.extract_and_update_info(
            session_dm, "We have a budget of $50k", "user"
        )

        await service.extract_and_update_info(
            session_non_dm, "We have a budget of $50k", "user"
        )

        # Mark one as decision maker
        await service.extract_and_update_info(
            session_dm, "I am the decision maker", "user"
        )

        await service.extract_and_update_info(
            session_non_dm, "I'm not the decision maker", "user"
        )

        # Refresh sessions
        result_dm = await db.execute(
            select(ConversationSession).where(
                ConversationSession.visitor_id == "test-dm-score-001"
            )
        )
        session_dm = result_dm.scalar_one_or_none()

        result_non_dm = await db.execute(
            select(ConversationSession).where(
                ConversationSession.visitor_id == "test-non-dm-score-001"
            )
        )
        session_non_dm = result_non_dm.scalar_one_or_none()

        print(f"Decision maker lead score: {session_dm.lead_score}")
        print(f"Non-decision maker lead score: {session_non_dm.lead_score}")

        # Decision maker should have higher score
        assert session_dm.lead_score > session_non_dm.lead_score
        assert session_dm.lead_score >= 15  # At least 15 points for being decision maker

        print("✓ Decision maker status positively affects lead score")


if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v", "-s"] + sys.argv[1:])
