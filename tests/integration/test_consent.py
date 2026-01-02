"""Test cases for GDPR consent functionality."""

import pytest
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.consent import Consent
from src.schemas.consent import ConsentCreate, ConsentResponse


@pytest.mark.asyncio
async def test_save_consent(db_session: AsyncSession):
    """Test saving user consent."""
    visitor_id = f"test_visitor_{uuid4().hex[:8]}"

    consent_data = ConsentCreate(
        visitor_id=visitor_id,
        accepted=True,
        declined=False,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0",
        data_collected="Personal information, business context, conversation data",
        legal_basis="Legitimate interest and contract initiation",
        retention_period="30 days from last activity"
    )

    # Test saving consent
    from src.api.routes.consent import save_consent
    response = await save_consent(consent_data, db_session)

    assert isinstance(response, ConsentResponse)
    assert response.visitor_id == visitor_id
    assert response.accepted is True
    assert response.declined is False
    assert response.version == "1.0"
    assert response.data_collected == consent_data.data_collected
    assert response.legal_basis == consent_data.legal_basis
    assert response.retention_period == consent_data.retention_period

    # Verify saved to database
    result = await db_session.execute(
        select(Consent).where(Consent.visitor_id == visitor_id)
    )
    consent = result.scalar_one()
    assert consent.visitor_id == visitor_id
    assert consent.accepted is True
    assert consent.declined is False


@pytest.mark.asyncio
async def test_get_consent(db_session: AsyncSession):
    """Test retrieving consent status."""
    visitor_id = f"test_visitor_{uuid4().hex[:8]}"

    # Create consent record
    consent = Consent(
        visitor_id=visitor_id,
        accepted=True,
        declined=False,
        timestamp=datetime.utcnow(),
        version="1.0",
        data_collected="Test data",
        legal_basis="Test legal basis",
        retention_period="30 days"
    )
    db_session.add(consent)
    await db_session.commit()
    await db_session.refresh(consent)

    # Test getting consent
    from src.api.routes.consent import get_consent
    response = await get_consent(visitor_id, db_session)

    assert isinstance(response, ConsentResponse)
    assert response.visitor_id == visitor_id
    assert response.accepted is True
    assert response.declined is False
    assert response.data_collected == "Test data"


@pytest.mark.asyncio
async def test_get_consent_not_found(db_session: AsyncSession):
    """Test getting consent for non-existent visitor."""
    visitor_id = f"nonexistent_{uuid4().hex[:8]}"

    from src.api.routes.consent import get_consent

    with pytest.raises(Exception) as exc_info:
        await get_consent(visitor_id, db_session)

    assert "No consent record found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_revoke_consent(db_session: AsyncSession):
    """Test revoking consent."""
    visitor_id = f"test_visitor_{uuid4().hex[:8]}"

    # Create consent record
    consent = Consent(
        visitor_id=visitor_id,
        accepted=True,
        declined=False,
        timestamp=datetime.utcnow(),
        version="1.0"
    )
    db_session.add(consent)
    await db_session.commit()
    await db_session.refresh(consent)

    # Test revoking consent
    from src.api.routes.consent import revoke_consent
    response = await revoke_consent(visitor_id, db_session)

    assert response == {"message": "Consent revoked successfully"}

    # Verify revoked in database
    await db_session.refresh(consent)
    assert consent.revoked is True
    assert consent.revoked_at is not None


@pytest.mark.asyncio
async def test_revoke_consent_not_found(db_session: AsyncSession):
    """Test revoking consent for non-existent visitor."""
    visitor_id = f"nonexistent_{uuid4().hex[:8]}"

    from src.api.routes.consent import revoke_consent

    with pytest.raises(Exception) as exc_info:
        await revoke_consent(visitor_id, db_session)

    assert "No consent record found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_multiple_consent_records(db_session: AsyncSession):
    """Test handling multiple consent records for same visitor."""
    visitor_id = f"test_visitor_{uuid4().hex[:8]}"

    # Create multiple consent records
    consent1 = Consent(
        visitor_id=visitor_id,
        accepted=False,
        declined=True,
        timestamp=datetime.utcnow(),
        version="1.0"
    )
    consent2 = Consent(
        visitor_id=visitor_id,
        accepted=True,
        declined=False,
        timestamp=datetime.utcnow(),
        version="1.0"
    )

    db_session.add_all([consent1, consent2])
    await db_session.commit()

    # Test getting latest consent (should return consent2)
    from src.api.routes.consent import get_consent
    response = await get_consent(visitor_id, db_session)

    assert response.accepted is True
    assert response.declined is False


@pytest.mark.asyncio
async def test_consent_data_validation(db_session: AsyncSession):
    """Test consent data validation."""
    visitor_id = f"test_visitor_{uuid4().hex[:8]}"

    # Test with minimal required fields
    consent_data = ConsentCreate(
        visitor_id=visitor_id,
        accepted=True,
        declined=False,
        timestamp=datetime.utcnow().isoformat()
    )

    from src.api.routes.consent import save_consent
    response = await save_consent(consent_data, db_session)

    assert response.visitor_id == visitor_id
    assert response.accepted is True
    assert response.declined is False
    assert response.version == "1.0"  # Should use default version
    assert response.data_collected is None  # Optional field
    assert response.legal_basis is None  # Optional field