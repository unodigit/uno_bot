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
from src.services.ai_service import AIService


class SessionService:
    """Service for managing conversation sessions and messages."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()

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
            content="🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nI can help you explore our services, understand your needs, and connect you with the right expert.\n\nTo get started, what's your name?",
            meta_data={"type": "welcome"},
            created_at=datetime.utcnow(),
        )
        self.db.add(welcome_message)
        await self.db.commit()

        # Refresh and eagerly load messages
        await self.db.refresh(session)
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.id == session.id)
            .options(selectinload(ConversationSession.messages))
        )
        return result.scalar_one()

    async def get_session(self, session_id: uuid.UUID) -> ConversationSession | None:
        """Get a session by ID."""
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.id == session_id)
            .options(
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
            meta_data=message_create.metadata or {},
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

    async def generate_ai_response(
        self, session: ConversationSession, user_message: str
    ) -> Message:
        """Generate AI response and add it to the session."""
        # Build conversation history
        conversation_history = []
        for msg in session.messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content,
            })

        # Extract user information from their response FIRST
        # This updates session data which is used for context
        await self._extract_user_info(session, user_message)

        # Build context with updated session data
        context = {
            "business_context": session.business_context,
            "client_info": session.client_info,
            "qualification": session.qualification,
            "current_phase": session.current_phase,
        }

        # Generate AI response
        ai_content = await self.ai_service.generate_response(
            user_message=user_message,
            conversation_history=conversation_history,
            context=context,
        )

        # Determine and update phase based on collected data
        new_phase = await self._determine_next_phase(session)
        if new_phase and new_phase != session.current_phase:
            await self.update_session_phase(session, new_phase)
            # Add phase change metadata to AI message
            meta_data = {"phase_change": new_phase}
        else:
            meta_data = {}

        # Create and save AI message
        ai_message = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=ai_content,
            meta_data=meta_data,
            created_at=datetime.utcnow(),
        )
        self.db.add(ai_message)
        await self.db.commit()
        await self.db.refresh(ai_message)

        return ai_message

    async def _extract_user_info(self, session: ConversationSession, user_message: str) -> None:
        """Extract user information from their responses and update session."""
        import re
        user_text = user_message.lower().strip()

        # Extract name (simple heuristic - if it's a greeting response)
        if not session.client_info.get("name"):
            # Look for patterns like "My name is John" or "I'm John" or "John"
            name_match = re.search(r"(?:my name is|i am|i'm)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)", user_text)
            if name_match:
                name = name_match.group(1).strip().title()
                if len(name) > 1 and len(name) < 50:  # Basic validation
                    await self.update_session_data(
                        session,
                        client_info={"name": name}
                    )
                    return

        # Extract email
        if not session.client_info.get("email"):
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, user_text)
            if email_match:
                email = email_match.group(0)
                await self.update_session_data(
                    session,
                    client_info={"email": email}
                )
                return

        # Extract company information
        if not session.client_info.get("company"):
            # Look for patterns like "I work at X", "company is X", "at X"
            company_patterns = [
                r"(?:work at|work for|company is|at)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?|I)",
                r"(?:my company|our company)\s+is\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)"
            ]
            for pattern in company_patterns:
                company_match = re.search(pattern, user_text)
                if company_match:
                    company = company_match.group(1).strip().title()
                    if len(company) > 2 and len(company) < 100:
                        await self.update_session_data(
                            session,
                            client_info={"company": company}
                        )
                        return

        # Extract business challenges
        if not session.business_context.get("challenges"):
            challenge_keywords = ['problem', 'issue', 'challenge', 'difficulty', 'struggle', 'pain', 'need', 'want', 'looking for', 'trying to']
            if any(keyword in user_text for keyword in challenge_keywords):
                await self.update_session_data(
                    session,
                    business_context={"challenges": user_message}
                )
                return

        # Extract industry
        if not session.business_context.get("industry"):
            industry_keywords = ['healthcare', 'finance', 'education', 'retail', 'manufacturing', 'tech', 'technology', 'software', 'e-commerce', 'ecommerce', 'saas', 'insurance', 'banking', 'logistics', 'construction', 'real estate']
            for keyword in industry_keywords:
                if keyword in user_text:
                    await self.update_session_data(
                        session,
                        business_context={"industry": keyword.title()}
                    )
                    return

        # Extract technology stack
        if not session.business_context.get("tech_stack"):
            tech_keywords = ['python', 'javascript', 'react', 'angular', 'vue', 'node', 'java', 'c#', 'dotnet', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'sql', 'mongodb', 'postgresql', 'mysql']
            found_tech = [tech for tech in tech_keywords if tech in user_text]
            if found_tech:
                await self.update_session_data(
                    session,
                    business_context={"tech_stack": ", ".join(found_tech)}
                )
                return

        # Extract budget range
        if not session.qualification.get("budget_range"):
            budget_patterns = {
                r"(under|less than|<)\s*\$?25,?000": "small (<$25k)",
                r"\$?25,?000\s*(to|-|and)\s*\$?100,?000": "medium ($25k-$100k)",
                r"(over|more than|>|>\s*\$?100,?000)": "large (>$100k)",
                r"small": "small (<$25k)",
                r"medium": "medium ($25k-$100k)",
                r"large": "large (>$100k)"
            }
            for pattern, value in budget_patterns.items():
                if re.search(pattern, user_text):
                    await self.update_session_data(
                        session,
                        qualification={"budget_range": value}
                    )
                    return

        # Extract timeline
        if not session.qualification.get("timeline"):
            timeline_patterns = {
                r"(urgent|immediate|asap|right away|soon|this month|within a month)": "urgent (<1 month)",
                r"(1-3 months|next month|couple months|within 3 months)": "near-term (1-3 months)",
                r"(3\+ months|long term|later|next quarter|6 months|next year)": "long-term (3+ months)"
            }
            for pattern, value in timeline_patterns.items():
                if re.search(pattern, user_text):
                    await self.update_session_data(
                        session,
                        qualification={"timeline": value}
                    )
                    return

        # Extract company size
        if not session.business_context.get("company_size"):
            size_patterns = {
                r"(startup|small|1-10|under 10|few people)": "1-10",
                r"(10-50|medium small|50 people)": "10-50",
                r"(50-200|medium|100 people)": "50-200",
                r"(200\+|large|enterprise|1000|big)": "200+"
            }
            for pattern, value in size_patterns.items():
                if re.search(pattern, user_text):
                    await self.update_session_data(
                        session,
                        business_context={"company_size": value}
                    )
                    return

        # Extract decision maker status
        if not session.qualification.get("is_decision_maker"):
            if "decision maker" in user_text or "i decide" in user_text or "i can decide" in user_text:
                await self.update_session_data(
                    session,
                    qualification={"is_decision_maker": True}
                )
                return
            elif "not the decision maker" in user_text or "need approval" in user_text or "boss" in user_text:
                await self.update_session_data(
                    session,
                    qualification={"is_decision_maker": False}
                )
                return

        # Check if we have enough info to calculate lead score and recommend service
        await self._calculate_lead_score(session)
        await self._recommend_service(session)

    async def _calculate_lead_score(self, session: ConversationSession) -> None:
        """Calculate lead score based on collected information."""
        score = 0

        # Client info points
        if session.client_info.get("name"):
            score += 10
        if session.client_info.get("email"):
            score += 15
        if session.client_info.get("company"):
            score += 10

        # Business context points
        if session.business_context.get("challenges"):
            score += 20
        if session.business_context.get("industry"):
            score += 10
        if session.business_context.get("company_size"):
            score += 10

        # Qualification points
        budget = session.qualification.get("budget_range")
        if budget:
            if "large" in budget:
                score += 25
            elif "medium" in budget:
                score += 20
            else:
                score += 15

        timeline = session.qualification.get("timeline")
        if timeline:
            if "urgent" in timeline:
                score += 20
            elif "near-term" in timeline:
                score += 15
            else:
                score += 10

        if session.qualification.get("is_decision_maker") is True:
            score += 15

        # Cap at 100
        score = min(score, 100)

        # Only update if we have meaningful data
        if score > 0:
            await self.update_session_data(session, lead_score=score)

    async def _recommend_service(self, session: ConversationSession) -> None:
        """Recommend appropriate service based on collected information."""
        if session.recommended_service:
            return

        # Get context
        challenges = session.business_context.get("challenges", "").lower()
        industry = session.business_context.get("industry", "").lower()
        tech_stack = session.business_context.get("tech_stack", "").lower()

        # Determine service based on keywords
        ai_keywords = ['ai', 'ml', 'machine learning', 'artificial intelligence', 'data', 'analytics', 'intelligence']
        dev_keywords = ['software', 'app', 'application', 'website', 'web', 'mobile', 'development', 'build', 'create']
        cloud_keywords = ['cloud', 'infrastructure', 'devops', 'deployment', 'server', 'aws', 'azure', 'gcp']
        strategy_keywords = ['strategy', 'consulting', 'planning', 'roadmap', 'digital transformation']

        content = challenges + " " + industry + " " + tech_stack

        # Score each service
        scores = {
            "AI Strategy & Planning": sum(1 for k in ai_keywords if k in content),
            "Custom Software Development": sum(1 for k in dev_keywords if k in content),
            "Cloud Infrastructure & DevOps": sum(1 for k in cloud_keywords if k in content),
            "Digital Transformation Consulting": sum(1 for k in strategy_keywords if k in content),
            "Data Intelligence & Analytics": sum(1 for k in ['data', 'analytics', 'insight'] if k in content)
        }

        # Get max score
        if scores:
            recommended = max(scores, key=scores.get)
            if scores[recommended] > 0:
                await self.update_session_data(session, recommended_service=recommended)
