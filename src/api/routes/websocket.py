"""WebSocket routes for real-time chat with Socket.IO."""
import logging
import uuid
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from socketio import AsyncServer

from src.core.config import settings
from src.models.session import MessageRole
from src.schemas.session import MessageCreate
from src.services.session_service import SessionService
from src.services.prd_service import PRDService
from src.services.expert_service import ExpertService

logger = logging.getLogger(__name__)

# Socket.IO server
sio = AsyncServer(
    cors_allowed_origins=settings.allowed_origins.split(","),
    async_mode="asgi",
    logger=True,
    engineio_logger=False,
)


class WebSocketManager:
    """Manages WebSocket connections and event handling."""

    def __init__(self):
        self.active_connections: Dict[str, Any] = {}

    def disconnect(self, session_id: str) -> None:
        """Disconnect a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")


# Global manager instance
manager = WebSocketManager()


async def handle_streaming_chat_message(
    session_id: str,
    content: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Handle incoming chat message and generate AI response with streaming.

    This function sends streaming events for real-time response updates.
    """
    session_service = SessionService(db)

    # Get the session
    session = await session_service.get_session(uuid.UUID(session_id))
    if not session:
        raise ValueError(f"Session {session_id} not found")

    # Add user message to database
    user_message = await session_service.add_message(
        uuid.UUID(session_id),
        MessageCreate(content=content),
        MessageRole.USER
    )

    # Update session activity
    await session_service.update_session_activity(session)

    # Build conversation history
    conversation_history = []
    for msg in session.messages:
        conversation_history.append({
            "role": msg.role,
            "content": msg.content,
        })

    # Extract user information from their response FIRST
    # This updates session data which is used for context
    await session_service._extract_user_info(session, content)

    # Check for ambiguous response AFTER extracting info
    ambiguity_check = await session_service._check_ambiguity(content, session)
    if ambiguity_check["is_ambiguous"]:
        # Generate clarification response instead of normal flow
        clarification_response = session_service._generate_clarification_response(
            ambiguity_check, content, session
        )

        # Create and save AI message with clarification
        ai_message = await session_service.add_message(
            uuid.UUID(session_id),
            MessageCreate(content=clarification_response),
            MessageRole.ASSISTANT,
            metadata={"type": "clarification", "ambiguous_reason": ambiguity_check["reason"]}
        )

        # Get updated session data
        session = await session_service.get_session(uuid.UUID(session_id))

        return {
            "user_message": {
                "id": str(user_message.id),
                "role": "user",
                "content": user_message.content,
                "created_at": user_message.created_at.isoformat(),
            },
            "ai_message": {
                "id": str(ai_message.id),
                "role": "assistant",
                "content": ai_message.content,
                "created_at": ai_message.created_at.isoformat(),
                "meta_data": ai_message.meta_data,
            },
            "session": {
                "current_phase": session.current_phase,
                "client_info": session.client_info,
                "business_context": session.business_context,
                "qualification": session.qualification,
                "lead_score": session.lead_score,
                "recommended_service": session.recommended_service,
                "matched_expert_id": str(session.matched_expert_id) if session.matched_expert_id else None,
                "prd_id": str(session.prd_id) if session.prd_id else None,
            }
        }

    # Calculate lead score and recommend service after each message
    await session_service._calculate_lead_score(session)
    await session_service._recommend_service(session)

    # Build context with updated session data
    context = {
        "business_context": session.business_context,
        "client_info": session.client_info,
        "qualification": session.qualification,
        "current_phase": session.current_phase,
    }

    # Generate AI response using streaming
    full_response = ""
    message_id = None

    # Send streaming response chunks
    async for chunk in session_service.ai_service.stream_response(
        content, conversation_history, context
    ):
        full_response += chunk

        # Send streaming event for each chunk
        from src.main import sio
        await sio.emit("streaming_message", {
            "chunk": chunk,
            "is_complete": False,
            "message_id": message_id
        }, room=session_id)

    # Create and save final AI message
    ai_message = await session_service.add_message(
        uuid.UUID(session_id),
        MessageCreate(content=full_response),
        MessageRole.ASSISTANT,
    )

    # Update message_id for the final message
    message_id = str(ai_message.id)

    # Determine and update phase based on collected data
    new_phase = await session_service._determine_next_phase(session)
    if new_phase and new_phase != session.current_phase:
        await session_service.update_session_phase(session, new_phase)

    # Get updated session data
    session = await session_service.get_session(uuid.UUID(session_id))

    # Send final streaming event
    from src.main import sio
    await sio.emit("streaming_message", {
        "chunk": "",
        "is_complete": True,
        "message_id": message_id
    }, room=session_id)

    return {
        "user_message": {
            "id": str(user_message.id),
            "role": "user",
            "content": user_message.content,
            "created_at": user_message.created_at.isoformat(),
        },
        "ai_message": {
            "id": str(ai_message.id),
            "role": "assistant",
            "content": ai_message.content,
            "created_at": ai_message.created_at.isoformat(),
            "meta_data": ai_message.meta_data,
        },
        "session": {
            "current_phase": session.current_phase,
            "client_info": session.client_info,
            "business_context": session.business_context,
            "qualification": session.qualification,
            "lead_score": session.lead_score,
            "recommended_service": session.recommended_service,
            "matched_expert_id": str(session.matched_expert_id) if session.matched_expert_id else None,
            "prd_id": str(session.prd_id) if session.prd_id else None,
        }
    }


async def handle_generate_prd(
    session_id: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Handle PRD generation request."""
    session_service = SessionService(db)
    prd_service = PRDService(db)

    # Get the session
    session = await session_service.get_session(uuid.UUID(session_id))
    if not session:
        raise ValueError(f"Session {session_id} not found")

    # Check if we have enough data
    if not session.client_info.get("name"):
        raise ValueError("Client name is required for PRD generation")

    if not session.business_context.get("challenges"):
        raise ValueError("Business challenges are required for PRD generation")

    # Generate PRD
    prd = await prd_service.generate_prd(session)

    # Get preview
    filename = prd_service.generate_filename(prd)
    preview_text = prd.content_markdown[:197] + "..." if len(prd.content_markdown) > 197 else prd.content_markdown

    return {
        "prd_id": str(prd.id),
        "filename": filename,
        "preview_text": preview_text,
        "version": prd.version,
        "storage_url": prd.storage_url,
    }


async def handle_match_experts(
    session_id: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Handle expert matching request."""
    session_service = SessionService(db)
    expert_service = ExpertService(db)

    # Get the session
    session = await session_service.get_session(uuid.UUID(session_id))
    if not session:
        raise ValueError(f"Session {session_id} not found")

    # Get matching experts
    matched_experts = await expert_service.match_experts(
        service_type=session.recommended_service,
        business_context=session.business_context,
    )

    # Format response
    experts = []
    scores = []
    for expert, score in matched_experts:
        experts.append({
            "id": str(expert.id),
            "name": expert.name,
            "email": expert.email,
            "role": expert.role,
            "bio": expert.bio,
            "photo_url": expert.photo_url,
            "specialties": expert.specialties,
            "services": expert.services,
            "is_active": expert.is_active,
        })
        scores.append(round(score, 1))

    # Update session with top expert
    if matched_experts:
        top_expert = matched_experts[0][0]
        session.matched_expert_id = top_expert.id
        db.add(session)
        await db.commit()

    return {
        "experts": experts,
        "match_scores": scores,
    }


async def handle_get_availability(
    expert_id: str,
    timezone: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Handle availability request."""
    from src.services.calendar_service import CalendarService

    expert_service = ExpertService(db)
    calendar_service = CalendarService()

    # Get expert
    expert = await expert_service.get_expert(uuid.UUID(expert_id))
    if not expert:
        raise ValueError(f"Expert {expert_id} not found")

    # Get availability
    slots = await calendar_service.get_availability(
        expert_id=expert_id,
        timezone=timezone,
        days_ahead=14,
    )

    return {
        "expert_id": expert_id,
        "expert_name": expert.name,
        "expert_role": expert.role,
        "timezone": timezone,
        "slots": slots,
    }


async def handle_create_booking(
    session_id: str,
    booking_data: Dict[str, Any],
    db: AsyncSession,
) -> Dict[str, Any]:
    """Handle booking creation."""
    from src.services.booking_service import BookingService

    booking_service = BookingService(db)
    session_service = SessionService(db)

    # Get the session
    session = await session_service.get_session(uuid.UUID(session_id))
    if not session:
        raise ValueError(f"Session {session_id} not found")

    # Create booking
    booking = await booking_service.create_booking(
        session_id=uuid.UUID(session_id),
        expert_id=uuid.UUID(booking_data["expert_id"]),
        start_time=booking_data["start_time"],
        end_time=booking_data["end_time"],
        timezone=booking_data["timezone"],
        client_name=booking_data["client_name"],
        client_email=booking_data["client_email"],
    )

    return {
        "booking_id": str(booking.id),
        "expert_id": str(booking.expert_id),
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "timezone": booking.timezone,
        "meeting_link": booking.meeting_link,
        "client_name": booking.client_name,
        "client_email": booking.client_email,
        "status": booking.status,
    }
