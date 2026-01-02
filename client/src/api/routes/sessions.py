"""Session and message API routes."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models import ConversationSession, Message
from src.schemas.session import (
    SessionCreate,
    SessionResponse,
    MessageCreate,
    MessageResponse,
    SessionResumeRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation session."""
    try:
        # Create session
        session = ConversationSession(
            visitor_id=session_data.visitor_id,
            source_url=session_data.source_url,
            user_agent=session_data.user_agent,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        logger.info(f"Created session {session.id} for visitor {session.visitor_id}")
        return session

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get session details and message history."""
    try:
        uuid = UUID(session_id)

        # Use select to get session
        result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == uuid)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Manually load messages
        messages_result = await db.execute(
            select(Message)
            .where(Message.session_id == uuid)
            .order_by(Message.created_at)
        )
        session.messages = messages_result.scalars().all()

        return session

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session"
        )


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    session_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a message to a session and get AI response."""
    try:
        uuid = UUID(session_id)

        # Verify session exists
        session_result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == uuid)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Add user message
        user_message = Message(
            session_id=uuid,
            role="user",
            content=message_data.content,
            metadata=message_data.metadata or {},
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        # Update session last activity
        session.last_activity = user_message.created_at
        await db.commit()

        # TODO: Integrate with AI service for response
        # For now, return a simple echo response
        bot_message = Message(
            session_id=uuid,
            role="assistant",
            content=f"I received your message: '{message_data.content}'. I'm currently in demo mode but will soon be connected to the AI engine.",
            metadata={"type": "demo"},
        )
        db.add(bot_message)
        await db.commit()
        await db.refresh(bot_message)

        logger.info(f"Added message to session {session_id}")
        return bot_message

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message"
        )


@router.post("/sessions/{session_id}/resume", response_model=SessionResponse)
async def resume_session(
    request: SessionResumeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resume an existing session."""
    try:
        session_id = request.session_id
        uuid = UUID(str(session_id))

        session_result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == uuid)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Update last activity
        await db.commit()
        await db.refresh(session)

        return session

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume session"
        )
