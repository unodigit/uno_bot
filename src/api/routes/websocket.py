"""WebSocket routes for real-time chat communication."""
import json
import logging
import uuid
from typing import Any, Dict

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.models.session import MessageRole
from src.schemas.session import MessageCreate, MessageResponse
from src.services.session_service import SessionService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and reconnections."""

    def __init__(self):
        # Store active connections: {session_id: {websocket: metadata}}
        self.active_connections: Dict[uuid.UUID, Dict[WebSocket, Dict[str, Any]]] = {}
        # Store connection attempts for reconnection handling
        self.reconnection_attempts: Dict[uuid.UUID, int] = {}

    async def connect(self, websocket: WebSocket, session_id: uuid.UUID) -> bool:
        """Connect a WebSocket to a session with reconnection logic."""
        await websocket.accept()

        # Check if this is a reconnection attempt
        if session_id in self.active_connections:
            # Check reconnection attempt limit
            max_reconnect_attempts = 5
            attempts = self.reconnection_attempts.get(session_id, 0)

            if attempts >= max_reconnect_attempts:
                logger.warning(f"Session {session_id} exceeded max reconnection attempts ({max_reconnect_attempts})")
                await websocket.close(code=4000, reason="Too many reconnection attempts")
                return False

            # Close existing connections for this session
            for existing_ws in list(self.active_connections[session_id].keys()):
                try:
                    await existing_ws.close(code=4001, reason="New connection established")
                except Exception as e:
                    logger.warning(f"Error closing existing WebSocket for session {session_id}: {e}")

            self.reconnection_attempts[session_id] = attempts + 1
            logger.info(f"Session {session_id} reconnected (attempt {attempts + 1}/{max_reconnect_attempts})")
        else:
            self.reconnection_attempts[session_id] = 0
            logger.info(f"New WebSocket connection for session {session_id}")

        # Add new connection
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}

        self.active_connections[session_id][websocket] = {
            "attempts": self.reconnection_attempts[session_id]
        }

        return True

    async def disconnect(self, websocket: WebSocket, session_id: uuid.UUID):
        """Disconnect a WebSocket connection."""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                del self.active_connections[session_id][websocket]

            # Clean up empty session entries
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                if session_id in self.reconnection_attempts:
                    del self.reconnection_attempts[session_id]

        logger.info(f"WebSocket disconnected for session {session_id}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            raise

    async def broadcast_to_session(self, session_id: uuid.UUID, message: Dict[str, Any]):
        """Broadcast a message to all WebSocket connections for a session."""
        if session_id in self.active_connections:
            disconnected_websockets = []

            for websocket in self.active_connections[session_id]:
                try:
                    await self.send_personal_message(message, websocket)
                except Exception:
                    # Mark for disconnection
                    disconnected_websockets.append(websocket)

            # Clean up disconnected websockets
            for websocket in disconnected_websockets:
                await self.disconnect(websocket, session_id)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket endpoint for real-time chat communication."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        await websocket.close(code=4000, reason="Invalid session ID format")
        return

    # Connect to session
    if not await manager.connect(websocket, session_uuid):
        return

    # Get database session
    async with get_db() as db:
        try:
            # Send connection confirmation
            await manager.send_personal_message({
                "type": "connected",
                "session_id": session_id,
                "message": "WebSocket connected successfully"
            }, websocket)

            # Main message handling loop
            while True:
                try:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message_data = json.loads(data)

                    # Validate message format
                    if not isinstance(message_data, dict):
                        await manager.send_personal_message({
                            "type": "error",
                            "error": "Invalid message format"
                        }, websocket)
                        continue

                    message_type = message_data.get("type")
                    content = message_data.get("content")

                    if message_type == "ping":
                        # Handle ping messages for connection health
                        await manager.send_personal_message({
                            "type": "pong",
                            "timestamp": "pong"
                        }, websocket)
                        continue

                    elif message_type == "message" and content:
                        # Handle user messages
                        await handle_user_message(
                            websocket,
                            session_uuid,
                            content,
                            db
                        )

                    else:
                        await manager.send_personal_message({
                            "type": "error",
                            "error": "Unknown message type or missing content"
                        }, websocket)

                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await manager.send_personal_message({
                        "type": "error",
                        "error": "Invalid JSON format"
                    }, websocket)
                except Exception as e:
                    logger.error(f"Error in WebSocket message handling: {e}")
                    await manager.send_personal_message({
                        "type": "error",
                        "error": f"Server error: {str(e)}"
                    }, websocket)

        finally:
            # Clean up on disconnect
            await manager.disconnect(websocket, session_uuid)


async def handle_user_message(
    websocket: WebSocket,
    session_id: uuid.UUID,
    content: str,
    db: AsyncSession
):
    """Handle incoming user messages and generate AI responses."""
    try:
        # Create message request
        message_create = MessageCreate(content=content)

        # Get session service
        service = SessionService(db)

        # Get session
        session = await service.get_session(session_id)
        if not session:
            await manager.send_personal_message({
                "type": "error",
                "error": f"Session {session_id} not found"
            }, websocket)
            return

        if session.status != "active":
            await manager.send_personal_message({
                "type": "error",
                "error": f"Cannot send message to {session.status} session"
            }, websocket)
            return

        # Add user message
        user_message = await service.add_message(
            session_id, message_create, MessageRole.USER
        )

        # Update session activity
        await service.update_session_activity(session)

        # Send user message confirmation
        await manager.send_personal_message({
            "type": "message_sent",
            "message": {
                "id": str(user_message.id),
                "session_id": str(user_message.session_id),
                "role": user_message.role,
                "content": user_message.content,
                "meta_data": user_message.meta_data,
                "created_at": user_message.created_at.isoformat()
            }
        }, websocket)

        # Generate AI response with streaming
        await generate_streaming_ai_response(session, session_id, websocket, db)

    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        await manager.send_personal_message({
            "type": "error",
            "error": f"Failed to process message: {str(e)}"
        }, websocket)


async def generate_streaming_ai_response(
    session,
    session_id: uuid.UUID,
    websocket: WebSocket,
    db: AsyncSession
):
    """Generate AI response with character-by-character streaming."""
    try:
        # Get session service
        service = SessionService(db)

        # Send typing indicator
        await manager.send_personal_message({
            "type": "typing_start",
            "session_id": str(session_id)
        }, websocket)

        # Generate response (this will be enhanced with actual AI integration)
        response_text = await service.generate_ai_response(session, "")

        # Stream response character by character
        streamed_message = await service.add_message(
            session_id,
            {"content": ""},  # Start with empty content
            MessageRole.ASSISTANT
        )

        # Send streaming response
        for i, char in enumerate(response_text):
            # Update message content incrementally
            partial_content = response_text[:i + 1]

            # Send streaming update
            await manager.send_personal_message({
                "type": "message_stream",
                "message": {
                    "id": str(streamed_message.id),
                    "session_id": str(session_id),
                    "role": "assistant",
                    "content": partial_content,
                    "is_complete": i == len(response_text) - 1,
                    "meta_data": {"streaming": True},
                    "created_at": streamed_message.created_at.isoformat()
                }
            }, websocket)

            # Small delay to simulate streaming
            import asyncio
            await asyncio.sleep(0.05)

        # Send typing stop indicator
        await manager.send_personal_message({
            "type": "typing_stop",
            "session_id": str(session_id)
        }, websocket)

    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        await manager.send_personal_message({
            "type": "error",
            "error": f"Failed to generate response: {str(e)}"
        }, websocket)