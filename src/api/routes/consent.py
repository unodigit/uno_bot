"""API routes for GDPR consent functionality."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.models.consent import Consent
from src.schemas.consent import ConsentCreate, ConsentResponse

router = APIRouter()


@router.post("/consent", response_model=ConsentResponse)
async def save_consent(
    consent_data: ConsentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Save user consent data.

    Args:
        consent_data: Consent information including accepted status, timestamp, and version
        db: Database session

    Returns:
        Saved consent record
    """
    try:
        # Create consent record
        consent = Consent(
            visitor_id=consent_data.visitor_id,
            accepted=consent_data.accepted,
            declined=consent_data.declined,
            timestamp=datetime.fromisoformat(consent_data.timestamp),
            version=consent_data.version,
            data_collected=consent_data.data_collected,
            legal_basis=consent_data.legal_basis,
            retention_period=consent_data.retention_period,
        )

        db.add(consent)
        await db.commit()
        await db.refresh(consent)

        return ConsentResponse(
            id=str(consent.id),
            visitor_id=consent.visitor_id,
            accepted=consent.accepted,
            declined=consent.declined,
            timestamp=consent.timestamp.isoformat(),
            version=consent.version,
            data_collected=consent.data_collected,
            legal_basis=consent.legal_basis,
            retention_period=consent.retention_period,
            created_at=consent.created_at.isoformat(),
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save consent: {str(e)}"
        ) from e


@router.get("/consent/{visitor_id}", response_model=ConsentResponse)
async def get_consent(
    visitor_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get consent status for a visitor.

    Args:
        visitor_id: Visitor UUID
        db: Database session

    Returns:
        Latest consent record for the visitor
    """
    try:
        # Get latest consent for visitor
        result = await db.execute(
            select(Consent)
            .where(Consent.visitor_id == visitor_id)
            .order_by(Consent.timestamp.desc())
            .limit(1)
        )
        consent = result.scalar_one_or_none()

        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No consent record found for this visitor"
            )

        return ConsentResponse(
            id=str(consent.id),
            visitor_id=consent.visitor_id,
            accepted=consent.accepted,
            declined=consent.declined,
            timestamp=consent.timestamp.isoformat(),
            version=consent.version,
            data_collected=consent.data_collected,
            legal_basis=consent.legal_basis,
            retention_period=consent.retention_period,
            created_at=consent.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve consent: {str(e)}"
        ) from e


@router.delete("/consent/{visitor_id}")
async def revoke_consent(
    visitor_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Revoke consent for a visitor (GDPR compliance).

    Args:
        visitor_id: Visitor UUID
        db: Database session

    Returns:
        Success message
    """
    try:
        # Mark consent as revoked
        result = await db.execute(
            select(Consent)
            .where(Consent.visitor_id == visitor_id)
            .order_by(Consent.timestamp.desc())
            .limit(1)
        )
        consent = result.scalar_one_or_none()

        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No consent record found for this visitor"
            )

        consent.revoked = True
        consent.revoked_at = datetime.utcnow()
        await db.commit()

        return {"message": "Consent revoked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke consent: {str(e)}"
        ) from e
