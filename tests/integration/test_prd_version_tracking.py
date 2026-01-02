"""Test PRD version tracking functionality."""
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.prd import PRDDocument
from src.models.session import ConversationSession
from src.schemas.session import SessionCreate
from src.services.prd_service import PRDService
from src.services.session_service import SessionService


@pytest.mark.asyncio
async def test_prd_version_tracking(db_session: AsyncSession):
    """Test that PRD regeneration creates a new version with incremented version number."""
    prd_service = PRDService(db_session)
    session_service = SessionService(db_session)

    # Create a test session
    session_create = SessionCreate(
        visitor_id="test_version_tracking",
        source_url="http://localhost:5173",
        user_agent="TestAgent/1.0"
    )
    session = await session_service.create_session(session_create)

    # Update session with required data
    from sqlalchemy.orm import selectinload
    result = await db_session.execute(
        select(ConversationSession)
        .options(selectinload(ConversationSession.messages))
        .where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {'name': 'John Doe', 'company': 'Test Corp'}
    session.business_context = {'challenges': 'Need AI strategy'}
    session.recommended_service = 'AI Strategy'
    session.matched_expert_id = uuid.uuid4()  # Mock expert ID
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Generate initial PRD
    prd_v1 = await prd_service.generate_prd(session=session)

    # Verify initial PRD
    assert prd_v1 is not None
    assert prd_v1.version == 1
    assert prd_v1.session_id == session.id
    assert prd_v1.client_company == 'Test Corp'
    assert prd_v1.client_name == 'John Doe'

    # Regenerate PRD (should create v2)
    prd_v2 = await prd_service.regenerate_prd(
        session=session,
        feedback='Please make it more detailed'
    )

    # Verify regenerated PRD
    assert prd_v2 is not None
    assert prd_v2.id != prd_v1.id, "Regenerated PRD should have a different ID"
    assert prd_v2.version == 2, "Version should be incremented"
    assert prd_v2.session_id == session.id
    assert prd_v2.content_markdown != prd_v1.content_markdown, "Content should be different"

    # Verify both PRDs exist in database
    result = await db_session.execute(
        select(PRDDocument).where(PRDDocument.session_id == session.id)
    )
    all_prds = result.scalars().all()

    assert len(all_prds) == 2, "Both PRD versions should exist in database"

    # Verify we can retrieve both versions
    prd_v1_retrieved = await prd_service.get_prd(prd_v1.id)
    prd_v2_retrieved = await prd_service.get_prd(prd_v2.id)

    assert prd_v1_retrieved is not None
    assert prd_v2_retrieved is not None
    assert prd_v1_retrieved.version == 1
    assert prd_v2_retrieved.version == 2


@pytest.mark.asyncio
async def test_prd_regeneration_without_feedback(db_session: AsyncSession):
    """Test PRD regeneration works without feedback parameter."""
    prd_service = PRDService(db_session)
    session_service = SessionService(db_session)

    # Create a test session
    session_create = SessionCreate(
        visitor_id="test_no_feedback",
        source_url="http://localhost:5173",
        user_agent="TestAgent/1.0"
    )
    session = await session_service.create_session(session_create)

    # Update session with required data
    from sqlalchemy.orm import selectinload
    result = await db_session.execute(
        select(ConversationSession)
        .options(selectinload(ConversationSession.messages))
        .where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {'name': 'Jane Doe', 'company': 'Another Corp'}
    session.business_context = {'challenges': 'Need data analytics'}
    session.recommended_service = 'Data Intelligence'
    session.matched_expert_id = uuid.uuid4()
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Generate initial PRD
    prd_v1 = await prd_service.generate_prd(session=session)

    # Regenerate without feedback
    prd_v2 = await prd_service.regenerate_prd(session=session)

    # Should still work and create new version
    assert prd_v2.id != prd_v1.id
    assert prd_v2.version == 2


@pytest.mark.asyncio
async def test_multiple_prd_regenerations(db_session: AsyncSession):
    """Test multiple consecutive PRD regenerations."""
    prd_service = PRDService(db_session)
    session_service = SessionService(db_session)

    # Create a test session
    session_create = SessionCreate(
        visitor_id="test_multi_version",
        source_url="http://localhost:5173",
        user_agent="TestAgent/1.0"
    )
    session = await session_service.create_session(session_create)

    # Update session with required data
    from sqlalchemy.orm import selectinload
    result = await db_session.execute(
        select(ConversationSession)
        .options(selectinload(ConversationSession.messages))
        .where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {'name': 'Bob Smith', 'company': 'Multi Version Corp'}
    session.business_context = {'challenges': 'Complex project'}
    session.recommended_service = 'Custom Software Development'
    session.matched_expert_id = uuid.uuid4()
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Generate v1
    prd_v1 = await prd_service.generate_prd(session=session)
    assert prd_v1.version == 1

    # Generate v2
    prd_v2 = await prd_service.regenerate_prd(session=session, feedback="More detail")
    assert prd_v2.version == 2

    # Generate v3
    prd_v3 = await prd_service.regenerate_prd(session=session, feedback="Even more detail")
    assert prd_v3.version == 3

    # Verify all three versions exist
    result = await db_session.execute(
        select(PRDDocument).where(PRDDocument.session_id == session.id)
    )
    all_prds = result.scalars().all()

    assert len(all_prds) == 3

    # Verify version numbers
    versions = {prd.version for prd in all_prds}
    assert versions == {1, 2, 3}


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        print("Testing PRD version tracking...")
        await test_prd_version_tracking()
        print("✓ test_prd_version_tracking passed")

        print("\nTesting PRD regeneration without feedback...")
        await test_prd_regeneration_without_feedback()
        print("✓ test_prd_regeneration_without_feedback passed")

        print("\nTesting multiple PRD regenerations...")
        await test_multiple_prd_regenerations()
        print("✓ test_multiple_prd_regenerations passed")

        print("\n✅ All PRD version tracking tests passed!")

    asyncio.run(run_tests())
