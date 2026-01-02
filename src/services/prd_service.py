"""PRD (Project Requirements Document) service for generation and management."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.prd import PRDDocument
from src.models.session import ConversationSession, Message
from src.services.ai_service import AIService


class PRDService:
    """Service for generating and managing Project Requirements Documents."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()

    async def generate_conversation_summary(self, session: ConversationSession) -> str:
        """Generate a conversation summary before PRD generation.

        Args:
            session: The conversation session

        Returns:
            The conversation summary text
        """
        # Build conversation history
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at)
        )
        messages = list(result.scalars().all())

        conversation_history = []
        for msg in messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Generate summary using AI service
        if not self.ai_service.llm:
            # Fallback summary
            return self._fallback_summary(session)

        prompt = f"""Generate a concise summary of this business discovery conversation.

Client Info:
{session.client_info}

Business Context:
{session.business_context}

Qualification:
{session.qualification}

Conversation History:
{conversation_history}

Please provide:
1. Key business challenges identified
2. Client's industry and company context
3. Budget range and timeline
4. Recommended service
5. Any important notes or next steps

Format as a clear, professional summary (3-5 bullet points)."""

        from langchain_core.messages import HumanMessage, SystemMessage
        try:
            response = await self.ai_service.llm.ainvoke([
                SystemMessage(content="You are an expert at summarizing business discovery conversations. Create concise, professional summaries."),
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception:
            return self._fallback_summary(session)

    def _fallback_summary(self, session: ConversationSession) -> str:
        """Fallback summary when AI service is unavailable."""
        name = session.client_info.get("name", "N/A")
        company = session.client_info.get("company", "N/A")
        industry = session.business_context.get("industry", "N/A")
        challenges = session.business_context.get("challenges", "N/A")
        budget = session.qualification.get("budget_range", "N/A")
        timeline = session.qualification.get("timeline", "N/A")
        service = session.recommended_service or "N/A"

        return f"""**Conversation Summary**

• **Client:** {name} from {company}
• **Industry:** {industry}
• **Challenges:** {challenges}
• **Budget:** {budget}
• **Timeline:** {timeline}
• **Recommended Service:** {service}"""

    async def generate_prd(self, session: ConversationSession, conversation_summary: str | None = None) -> PRDDocument:
        """Generate a PRD for a session.

        Args:
            session: The conversation session to generate PRD for
            conversation_summary: Optional pre-approved conversation summary

        Returns:
            The generated PRD document
        """
        # Check if PRD already exists
        if session.prd_id:
            existing_prd = await self.get_prd(session.prd_id)
            if existing_prd:
                return existing_prd

        # Build conversation history - always load messages explicitly
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at)
        )
        messages = list(result.scalars().all())

        conversation_history = []
        for msg in messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Use provided summary or generate one
        if not conversation_summary:
            conversation_summary = await self.generate_conversation_summary(session)

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
            conversation_summary=conversation_summary,
            client_company=session.client_info.get("company"),
            client_name=session.client_info.get("name"),
            recommended_service=session.recommended_service,
            matched_expert_id=session.matched_expert_id,
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
        await self.db.merge(session)
        await self.db.commit()

        # Invalidate cache
        from src.services.cache_service import delete_cached_session_data
        await delete_cached_session_data(str(session.id))

        return prd

    async def get_prd(self, prd_id: uuid.UUID) -> PRDDocument | None:
        """Get a PRD by ID.

        Args:
            prd_id: The PRD ID

        Returns:
            The PRD document or None if not found
        """
        result = await self.db.execute(
            select(PRDDocument)
            .where(PRDDocument.id == prd_id)
            .options(selectinload(PRDDocument.expert))
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
            select(PRDDocument)
            .where(PRDDocument.session_id == session_id)
            .options(selectinload(PRDDocument.expert))
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
        existing_summary = None
        if session.prd_id:
            existing_prd = await self.get_prd(session.prd_id)
            if existing_prd:
                existing_version = existing_prd.version
                existing_summary = existing_prd.conversation_summary

        # Build conversation history - always load messages explicitly
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at)
        )
        messages = list(result.scalars().all())

        conversation_history = []
        for msg in messages:
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
            conversation_summary=existing_summary,
            client_company=session.client_info.get("company"),
            client_name=session.client_info.get("name"),
            recommended_service=session.recommended_service,
            matched_expert_id=session.matched_expert_id,
            version=existing_version + 1
        )

        self.db.add(new_prd)
        await self.db.commit()
        await self.db.refresh(new_prd)

        # Update storage_url with unique PRD ID (after we have the prd.id)
        new_prd.storage_url = f"/api/v1/prd/{new_prd.id}/download"
        self.db.add(new_prd)
        await self.db.commit()
        await self.db.refresh(new_prd)

        # Update session with new PRD ID
        session.prd_id = new_prd.id
        await self.db.merge(session)
        await self.db.commit()

        # Invalidate cache
        from src.services.cache_service import delete_cached_session_data
        await delete_cached_session_data(str(session.id))

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
