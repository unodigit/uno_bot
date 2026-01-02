"""Session and message service layer for business logic."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.session import (
    ConversationSession,
    Message,
    MessageRole,
    SessionPhase,
    SessionStatus,
)
from src.schemas.session import MessageCreate, SessionCreate


class SessionService:
    """Service for managing conversation sessions and messages."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, session_create: SessionCreate) -> ConversationSession:
        """Create a new conversation session."""
        session = ConversationSession(
            visitor_id=session_create.visitor_id,
            source_url=session_create.source_url,
            user_agent=session_create.user_agent,
            status=SessionStatus.ACTIVE,
            current_phase=SessionPhase.GREETING,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.flush()

        # Add initial welcome message
        welcome_message = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content="Hello! I'm UnoBot, your AI business consultant. I can help you explore our services, understand your needs, and connect you with the right expert. How can I help you today?",
            metadata={"type": "welcome"},
            created_at=datetime.utcnow(),
        )
        self.db.add(welcome_message)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: uuid.UUID) -> ConversationSession | None:
        """Get a session by ID."""
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.id == session_id)
            .options(
                selectinload(ConversationSession.matched_expert),
                selectinload(ConversationSession.messages),
            )
        )
        return result.scalar_one_or_none()

    async def update_session_activity(self, session: ConversationSession) -> None:
        """Update the last activity timestamp of a session."""
        session.last_activity = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()

    async def add_message(
        self, session_id: uuid.UUID, message_create: MessageCreate, role: MessageRole
    ) -> Message:
        """Add a message to a session."""
        message = Message(
            session_id=session_id,
            role=role,
            content=message_create.content,
            metadata=message_create.metadata or {},
            created_at=datetime.utcnow(),
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_session_messages(self, session_id: uuid.UUID) -> list[Message]:
        """Get all messages for a session."""
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def resume_session(self, session: ConversationSession) -> ConversationSession:
        """Resume an existing session."""
        session.status = SessionStatus.ACTIVE
        session.last_activity = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def complete_session(self, session: ConversationSession) -> ConversationSession:
        """Mark a session as completed."""
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def update_session_phase(
        self, session: ConversationSession, phase: SessionPhase
    ) -> None:
        """Update the current phase of a session."""
        session.current_phase = phase.value
        self.db.add(session)
        await self.db.commit()

    async def update_session_data(
        self,
        session: ConversationSession,
        client_info: dict[str, Any] | None = None,
        business_context: dict[str, Any] | None = None,
        qualification: dict[str, Any] | None = None,
        lead_score: int | None = None,
        recommended_service: str | None = None,
    ) -> None:
        """Update session data fields."""
        if client_info:
            session.client_info = {**session.client_info, **client_info}
        if business_context:
            session.business_context = {**session.business_context, **business_context}
        if qualification:
            session.qualification = {**session.qualification, **qualification}
        if lead_score is not None:
            session.lead_score = lead_score
        if recommended_service:
            session.recommended_service = recommended_service

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
