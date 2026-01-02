"""PRD (Project Requirements Document) service for generation and management."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.prd import PRDDocument
from src.models.session import ConversationSession
from src.services.ai_service import AIService


class PRDService:
    """Service for generating and managing Project Requirements Documents."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()

    async def generate_prd(self, session: ConversationSession) -> PRDDocument:
        """Generate a PRD for a session.

        Args:
            session: The conversation session to generate PRD for

        Returns:
            The generated PRD document
        """
        # Check if PRD already exists
        if session.prd_id:
            existing_prd = await self.get_prd(session.prd_id)
            if existing_prd:
                return existing_prd

        # Build conversation history
        conversation_history = []
        for msg in session.messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Generate PRD content using AI service
        prd_content = await self.ai_service.generate_prd(
            business_context=session.business_context,
            client_info=session.client_info,
            conversation_history=conversation_history
        )

        # Create PRD document
        prd = PRDDocument(
            session_id=session.id,
            content_markdown=prd_content,
            client_company=session.client_info.get("company"),
            client_name=session.client_info.get("name"),
            recommended_service=session.recommended_service,
            matched_expert=session.matched_expert_id,
        )

        self.db.add(prd)
        await self.db.commit()
        await self.db.refresh(prd)

        # Update storage_url with unique PRD ID (after we have the prd.id)
        prd.storage_url = f"/api/v1/prd/{prd.id}/download"
        self.db.add(prd)
        await self.db.commit()
        await self.db.refresh(prd)

        # Update session with PRD ID
        session.prd_id = prd.id
        self.db.add(session)
        await self.db.commit()

        return prd

    async def get_prd(self, prd_id: uuid.UUID) -> PRDDocument | None:
        """Get a PRD by ID.

        Args:
            prd_id: The PRD ID

        Returns:
            The PRD document or None if not found
        """
        result = await self.db.execute(
            select(PRDDocument).where(PRDDocument.id == prd_id)
        )
        return result.scalar_one_or_none()

    async def get_prd_by_session(self, session_id: uuid.UUID) -> PRDDocument | None:
        """Get PRD by session ID.

        Args:
            session_id: The session ID

        Returns:
            The PRD document or None if not found
        """
        result = await self.db.execute(
            select(PRDDocument).where(PRDDocument.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def increment_download_count(self, prd: PRDDocument) -> None:
        """Increment download count for a PRD.

        Args:
            prd: The PRD document
        """
        prd.increment_download()
        self.db.add(prd)
        await self.db.commit()
        await self.db.refresh(prd)

    async def regenerate_prd(
        self,
        session: ConversationSession,
        feedback: str | None = None
    ) -> PRDDocument:
        """Regenerate a PRD with optional feedback.

        Args:
            session: The conversation session
            feedback: Optional feedback for regeneration

        Returns:
            The new PRD document
        """
        # Get existing PRD version if any
        existing_version = 1
        if session.prd_id:
            existing_prd = await self.get_prd(session.prd_id)
            if existing_prd:
                existing_version = existing_prd.version

        # Build conversation history
        conversation_history = []
        for msg in session.messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Generate new PRD content using AI service
        prd_content = await self.ai_service.generate_prd(
            business_context=session.business_context,
            client_info=session.client_info,
            conversation_history=conversation_history,
            feedback=feedback
        )

        # Create new PRD document with incremented version
        new_prd = PRDDocument(
            session_id=session.id,
            content_markdown=prd_content,
            client_company=session.client_info.get("company"),
            client_name=session.client_info.get("name"),
            recommended_service=session.recommended_service,
            matched_expert=session.matched_expert_id,
            storage_url=f"/api/v1/prd/{session.id}/download",
            version=existing_version + 1
        )

        self.db.add(new_prd)
        await self.db.commit()
        await self.db.refresh(new_prd)

        # Update session with new PRD ID
        session.prd_id = new_prd.id
        self.db.add(session)
        await self.db.commit()

        return new_prd

    def generate_filename(self, prd: PRDDocument) -> str:
        """Generate a filename for the PRD download.

        Args:
            prd: The PRD document

        Returns:
            Filename in format: PRD_{company}_{date}_v{version}.md
        """
        company = prd.client_company or "Project"
        date = prd.created_at.strftime("%Y%m%d")
        return f"PRD_{company}_{date}_v{prd.version}.md"
