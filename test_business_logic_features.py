"""
Comprehensive test for business logic features:
- Feature 187: Decision maker identification is collected
- Feature 188: Success criteria collection works
- Feature 189: Intent detection identifies visitor needs
- Feature 190: Context retention works across long conversations
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from src.main import app
from src.core.database import get_db
from src.models import ConversationSession, Message
from src.services.session_service import SessionService
import json


@pytest.mark.asyncio
async def test_decision_maker_identification():
    """
    Feature 187: Decision maker identification is collected
    Steps:
    1. Progress to qualification phase
    2. Answer decision maker question
    3. Verify response stored
    4. Verify affects lead score
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Create session and provide basic info
        response = await client.post(
            "/api/v1/sessions",
            json={"visitor_id": "test-decision-maker-visitor"}
        )
        assert response.status_code == 201
        session_id = response.json()["visitor_id"]

        # Provide name and email
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "Hi, I'm John Smith from Acme Corp"}
        )

        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "john@acmecorp.com"}
        )

        # Step 2: Answer decision maker question positively
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "I'm the decision maker for this project"}
        )

        # Step 3: Verify response stored
        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            qualification = session.qualification or {}
            assert qualification.get("is_decision_maker") is True

        # Step 4: Verify affects lead score (decision maker adds 15 points)
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "Our budget is around $50k"}
        )

        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()
            lead_score = session.lead_score or 0

            # Should have at least 15 points from being decision maker
            assert lead_score >= 15

        print("✓ Feature 187: Decision maker identification collected and affects lead score")


@pytest.mark.asyncio
async def test_decision_maker_negative():
    """Test that non-decision maker status is also captured"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sessions",
            json={"visitor_id": "test-non-decision-maker-visitor"}
        )
        session_id = response.json()["visitor_id"]

        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "Hi, I'm Jane from Acme Corp"}
        )

        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "I'm not the decision maker, I need boss approval"}
        )

        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            qualification = session.qualification or {}
            assert qualification.get("is_decision_maker") is False

        print("✓ Non-decision maker status correctly captured")


@pytest.mark.asyncio
async def test_success_criteria_collection():
    """
    Feature 188: Success criteria collection works
    Steps:
    1. Progress conversation
    2. Define success criteria
    3. Verify captured in context
    4. Verify included in PRD
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Create session
        response = await client.post("/api/v1/sessions", json={"visitor_id": "test-visitor-xyz"})
        session_id = response.json()["visitor_id"]

        # Provide basic info
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "Hi, I'm Mike from TechStartup Inc"}
        )

        # Step 2: Define success criteria
        success_message = (
            "Our success criteria are: "
            "1. Reduce processing time by 50%, "
            "2. Handle 1000 concurrent users, "
            "3. Achieve 99.9% uptime"
        )

        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": success_message}
        )

        # Step 3: Verify captured in context
        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            qualification = session.qualification or {}
            success_criteria = qualification.get("success_criteria", "")

            # Should contain keywords from the message
            assert "reduce" in success_criteria.lower() or "processing" in success_criteria.lower()
            assert len(success_criteria) > 0

        print("✓ Feature 188: Success criteria captured in qualification")


@pytest.mark.asyncio
async def test_intent_detection():
    """
    Feature 189: Intent detection identifies visitor needs
    Steps:
    1. Start conversation
    2. Express a specific need
    3. Verify intent is detected
    4. Verify conversation adapts
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Start conversation
        response = await client.post("/api/v1/sessions", json={"visitor_id": "test-visitor-xyz"})
        session_id = response.json()["visitor_id"]

        # Step 2: Express specific need - AI development
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "We need help building an AI-powered recommendation engine"}
        )

        # Give time for processing
        await asyncio.sleep(1)

        # Step 3: Verify intent detected in business context
        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            business_context = session.business_context or {}
            challenges = business_context.get("challenges", "")

            # Should have captured the challenge
            assert len(challenges) > 0
            assert "ai" in challenges.lower() or "recommendation" in challenges.lower()

        # Step 4: Verify service recommendation matches intent
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "My email is sarah@techstartup.com"}
        )

        await asyncio.sleep(1)

        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            # Should recommend AI Strategy or similar
            recommended_service = session.recommended_service
            assert recommended_service is not None
            # AI-related needs should get AI or data-related service
            assert any(keyword in recommended_service.lower()
                      for keyword in ["ai", "data", "intelligence"])

        print("✓ Feature 189: Intent detection working and conversation adapts")


@pytest.mark.asyncio
async def test_context_retention():
    """
    Feature 190: Context retention works across long conversations
    Steps:
    1. Have 15+ message conversation
    2. Reference earlier information
    3. Verify bot remembers context
    4. Verify no context confusion
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Create long conversation
        response = await client.post("/api/v1/sessions", json={"visitor_id": "test-visitor-xyz"})
        session_id = response.json()["visitor_id"]

        messages = [
            "Hi, I'm David from LogisticsCorp",
            "david@logisticscorp.com",
            "We're in the logistics industry",
            "We use Python and PostgreSQL currently",
            "Our challenge is route optimization",
            "Budget is around $100k",
            "We need this done in 3 months",
            "I'm the decision maker",
            "We want to reduce fuel costs by 20%",
            "Currently using legacy systems",
            "Need real-time tracking",
            "Scale to 10,000 vehicles",
            "Cloud-based solution preferred",
            "Need mobile app for drivers",
            "Integration with ERP required",
            "Success measured by cost reduction",
            "What did you say about our industry?",  # Reference earlier info
        ]

        # Send all messages
        for msg in messages:
            await client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json={"content": msg}
            )
            await asyncio.sleep(0.2)  # Small delay between messages

        # Wait for final processing
        await asyncio.sleep(2)

        # Step 2 & 3: Verify bot remembers earlier context (industry mentioned in message 3)
        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            business_context = session.business_context or {}

            # Should remember industry mentioned earlier
            assert business_context.get("industry") == "Logistics"
            # Should remember tech stack
            assert "python" in business_context.get("tech_stack", "").lower()
            # Should remember challenge
            assert "route" in business_context.get("challenges", "").lower()

            # Should have all qualification data
            qualification = session.qualification or {}
            assert qualification.get("budget_range") is not None
            assert qualification.get("timeline") is not None
            assert qualification.get("is_decision_maker") is True
            assert "cost" in qualification.get("success_criteria", "").lower()

            # Should have recommended service
            assert session.recommended_service is not None

            # Should have calculated lead score
            assert session.lead_score > 0

        # Step 4: Verify no context confusion - check database state consistency
        async with get_db() as db:
            result = await db.execute(
                select(Message).where(
                    Message.session_id == session.id
                ).order_by(Message.created_at)
            )
            messages_db = result.scalars().all()

            # Should have all messages stored
            assert len(messages_db) >= len(messages)

            # Check last message references earlier context
            last_message = messages_db[-1]
            assert "industry" in last_message.content.lower()

        print("✓ Feature 190: Context retention works across long conversations")


@pytest.mark.asyncio
async def test_industry_detection():
    """Test industry detection from various keywords"""
    test_cases = [
        ("We're in healthcare", "Healthcare"),
        ("Working in finance sector", "Finance"),
        ("Education company", "Education"),
        ("Retail business", "Retail"),
        ("Manufacturing plant", "Manufacturing"),
        ("Tech startup", "Tech"),
        ("SaaS company", "Saas"),
    ]

    for message, expected_industry in test_cases:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/sessions", json={"visitor_id": "test-visitor-xyz"})
            session_id = response.json()["visitor_id"]

            await client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json={"content": message}
            )

            await asyncio.sleep(0.5)

            async with get_db() as db:
                result = await db.execute(
                    select(ConversationSession).where(
                        ConversationSession.visitor_id == session_id
                    )
                )
                session = result.scalar_one_or_none()

                assert session is not None
                business_context = session.business_context or {}
                detected_industry = business_context.get("industry", "")

                # Check if industry was detected
                assert len(detected_industry) > 0

                print(f"  ✓ '{message}' -> Industry: '{detected_industry}'")


@pytest.mark.asyncio
async def test_tech_stack_detection():
    """Test technology stack detection"""
    message = "Our stack includes Python, React, and AWS"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/sessions", json={"visitor_id": "test-visitor-xyz"})
        session_id = response.json()["visitor_id"]

        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": message}
        )

        await asyncio.sleep(0.5)

        async with get_db() as db:
            result = await db.execute(
                select(ConversationSession).where(
                    ConversationSession.visitor_id == session_id
                )
            )
            session = result.scalar_one_or_none()

            assert session is not None
            business_context = session.business_context or {}
            tech_stack = business_context.get("tech_stack", "").lower()

            assert "python" in tech_stack
            assert "react" in tech_stack
            assert "aws" in tech_stack

        print("✓ Technology stack detection working")


if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v", "-s"] + sys.argv[1:])
