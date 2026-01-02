"""Session and message service layer for business logic."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.security import sanitize_input, validate_sql_input
from src.models.session import (
    ConversationSession,
    Message,
    MessageRole,
    SessionPhase,
    SessionStatus,
)
from src.schemas.session import MessageCreate, SessionCreate
from src.services.ai_service import AIService
from src.services.expert_service import ExpertService
from src.services.template_service import TemplateService
from src.services.cache_service import cache_session_data, get_cached_session_data, delete_cached_session_data


class SessionService:
    """Service for managing conversation sessions and messages."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
        self.template_service = TemplateService(db)

    async def create_session(self, session_create: SessionCreate) -> ConversationSession:
        """Create a new conversation session with sanitized inputs."""
        # Sanitize string inputs
        sanitized_visitor_id = sanitize_input(session_create.visitor_id)
        sanitized_source_url = sanitize_input(session_create.source_url)
        sanitized_user_agent = sanitize_input(session_create.user_agent)

        session = ConversationSession(
            visitor_id=sanitized_visitor_id,
            source_url=sanitized_source_url,
            user_agent=sanitized_user_agent,
            status=SessionStatus.ACTIVE,
            current_phase=SessionPhase.GREETING,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.flush()

        # Get welcome message from template service
        # Try to get a template based on context (could extract industry from source_url in future)
        template = await self.template_service.get_template_for_industry(None)

        if template:
            welcome_content = template.content
            # Increment use count
            await self.template_service.increment_use_count(template.id)
        else:
            # Fallback to default message
            welcome_content = "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nI can help you explore our services, understand your needs, and connect you with the right expert.\n\nTo get started, what's your name?"

        # Add initial welcome message
        welcome_message = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=welcome_content,
            meta_data={
                "type": "welcome",
                "template_id": str(template.id) if template else None,
            },
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

    async def get_session(self, session_id: uuid.UUID, skip_cache: bool = False) -> ConversationSession | None:
        """Get a session by ID with caching.

        Args:
            session_id: The session ID to retrieve
            skip_cache: If True, bypass the cache and fetch from database directly
        """
        # Try to get from cache first (unless skipped)
        if not skip_cache:
            cached_session = await get_cached_session_data(str(session_id))
            if cached_session:
                # Reconstruct the session object from cached data
                return self._reconstruct_session_from_cache(cached_session)

        # If not cached (or cache skipped), get from database
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.id == session_id)
            .options(
                selectinload(ConversationSession.messages),
            )
        )
        session = result.scalar_one_or_none()

        # Cache the session data if found (and cache not skipped)
        if session and not skip_cache:
            await cache_session_data(
                str(session_id),
                {
                    "id": str(session.id),
                    "visitor_id": session.visitor_id,
                    "status": session.status,
                    "current_phase": session.current_phase,
                    "client_info": session.client_info,
                    "business_context": session.business_context,
                    "qualification": session.qualification,
                    "email_opt_in": session.email_opt_in,
                    "email_preferences": session.email_preferences,
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "source_url": session.source_url,
                    "user_agent": session.user_agent,
                    "lead_score": session.lead_score,
                    "recommended_service": session.recommended_service,
                    "matched_expert_id": str(session.matched_expert_id) if session.matched_expert_id else None,
                    "prd_id": str(session.prd_id) if session.prd_id else None,
                    "booking_id": str(session.booking_id) if session.booking_id else None,
                    "messages": [
                        {
                            "id": str(m.id),
                            "role": m.role,
                            "content": m.content,
                            "meta_data": m.meta_data,
                            "created_at": m.created_at.isoformat()
                        }
                        for m in session.messages
                    ]
                }
            )

        return session

    def _reconstruct_session_from_cache(self, cached_data: dict) -> ConversationSession:
        """Reconstruct a ConversationSession object from cached data."""
        from src.models.session import SessionStatus, SessionPhase, MessageRole, Message
        import uuid
        from datetime import datetime

        # Parse timestamps from cache
        started_at = datetime.fromisoformat(cached_data["started_at"]) if cached_data.get("started_at") else datetime.utcnow()
        last_activity = datetime.fromisoformat(cached_data["last_activity"]) if cached_data.get("last_activity") else datetime.utcnow()
        completed_at = datetime.fromisoformat(cached_data["completed_at"]) if cached_data.get("completed_at") else None

        # Create a mock session object with cached data
        session = ConversationSession(
            id=uuid.UUID(cached_data["id"]),
            visitor_id=cached_data["visitor_id"],
            status=SessionStatus(cached_data["status"]),
            current_phase=SessionPhase(cached_data["current_phase"]),
            client_info=cached_data["client_info"],
            business_context=cached_data["business_context"],
            qualification=cached_data["qualification"],
            email_opt_in=cached_data.get("email_opt_in", False),
            email_preferences=cached_data.get("email_preferences", {}),
            started_at=started_at,
            last_activity=last_activity,
            completed_at=completed_at,
            source_url=cached_data.get("source_url"),
            user_agent=cached_data.get("user_agent"),
            lead_score=cached_data.get("lead_score"),
            recommended_service=cached_data.get("recommended_service"),
            matched_expert_id=uuid.UUID(cached_data["matched_expert_id"]) if cached_data.get("matched_expert_id") else None,
            prd_id=uuid.UUID(cached_data["prd_id"]) if cached_data.get("prd_id") else None,
            booking_id=uuid.UUID(cached_data["booking_id"]) if cached_data.get("booking_id") else None,
        )

        # Add cached messages
        for msg_data in cached_data["messages"]:
            message = Message(
                id=uuid.UUID(msg_data["id"]),
                session_id=session.id,
                role=MessageRole(msg_data["role"]),
                content=msg_data["content"],
                meta_data=msg_data["meta_data"],
                created_at=datetime.fromisoformat(msg_data["created_at"]),
            )
            session.messages.append(message)

        return session

    async def update_session_activity(self, session: ConversationSession) -> None:
        """Update the last activity timestamp of a session."""
        session.last_activity = datetime.utcnow()
        merged_session = await self.db.merge(session)
        await self.db.commit()
        # Invalidate cache
        await delete_cached_session_data(str(merged_session.id))

    async def add_message(
        self, session_id: uuid.UUID, message_create: MessageCreate, role: MessageRole
    ) -> Message:
        """Add a message to a session with input sanitization."""
        # Sanitize content to prevent XSS
        sanitized_content = sanitize_input(message_create.content)

        # Validate against SQL injection
        if not validate_sql_input(sanitized_content):
            raise ValueError("Invalid content detected")

        message = Message(
            session_id=session_id,
            role=role,
            content=sanitized_content,
            meta_data=message_create.metadata or {},
            created_at=datetime.utcnow(),
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        # Invalidate cache
        await delete_cached_session_data(str(session_id))
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
        merged_session = await self.db.merge(session)
        await self.db.commit()
        await self.db.refresh(merged_session)
        # Reload messages after refresh
        await self.db.refresh(merged_session, attribute_names=["messages"])
        # Invalidate cache
        await delete_cached_session_data(str(merged_session.id))
        return merged_session

    async def complete_session(self, session: ConversationSession) -> ConversationSession:
        """Mark a session as completed."""
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        merged_session = await self.db.merge(session)
        await self.db.commit()
        await self.db.refresh(merged_session)
        # Invalidate cache
        await delete_cached_session_data(str(merged_session.id))
        return merged_session

    async def update_session_phase(
        self, session: ConversationSession, phase: SessionPhase
    ) -> None:
        """Update the current phase of a session."""
        session.current_phase = phase.value
        merged_session = await self.db.merge(session)
        await self.db.commit()
        # Invalidate cache
        await delete_cached_session_data(str(merged_session.id))

    async def update_session_data(
        self,
        session: ConversationSession,
        client_info: dict[str, Any] | None = None,
        business_context: dict[str, Any] | None = None,
        qualification: dict[str, Any] | None = None,
        lead_score: int | None = None,
        recommended_service: str | None = None,
    ) -> ConversationSession:
        """Update session data fields.

        Returns the updated session.
        """
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

        # Use merge() to handle both attached and detached objects
        # This is needed because cached sessions are detached
        merged_session = await self.db.merge(session)
        await self.db.commit()
        await self.db.refresh(merged_session)

        # Invalidate cache after update
        await delete_cached_session_data(str(merged_session.id))

        return merged_session

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
        # Always extract, even if the response is ambiguous
        await self._extract_user_info(session, user_message)

        # Check for ambiguous response AFTER extracting info
        ambiguity_check = await self._check_ambiguity(user_message, session)
        if ambiguity_check["is_ambiguous"]:
            # Generate clarification response instead of normal flow
            clarification_response = self._generate_clarification_response(
                ambiguity_check, user_message, session
            )

            # Create and save AI message with clarification
            ai_message = Message(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=clarification_response,
                meta_data={"type": "clarification", "ambiguous_reason": ambiguity_check["reason"]},
                created_at=datetime.utcnow(),
            )
            self.db.add(ai_message)
            await self.db.commit()
            await self.db.refresh(ai_message)
            return ai_message

        # Calculate lead score and recommend service after each message
        # This ensures it runs even if extraction returns early
        await self._calculate_lead_score(session)
        await self._recommend_service(session)

        # Build context with updated session data
        context = {
            "business_context": session.business_context,
            "client_info": session.client_info,
            "qualification": session.qualification,
            "current_phase": session.current_phase,
        }

        # Generate AI response using streaming
        ai_content = await self._generate_streaming_response(
            user_message, conversation_history, context
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
            # Look for patterns like "My name is John Doe" or "I'm John Doe" or "John Doe"
            # Capture full names (multiple words) until we hit punctuation or common stop words
            name_match = re.search(r"(?:my name is|i am|i'm)\s+([a-zA-Z\s]+?)(?:\s+(?:and|but|or|with|from|at|in|to|for|on|about|my|our|we|i)|[,.!?]|$)", user_text)
            if name_match:
                name = sanitize_input(name_match.group(1).strip().title())
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
                email = sanitize_input(email_match.group(0))
                await self.update_session_data(
                    session,
                    client_info={"email": email}
                )
                return

        # Extract company information
        if not session.client_info.get("company"):
            # Look for patterns like "I work at X", "company is X", "at X", "company is called X"
            company_patterns = [
                r"(?:work at|work for)\s+([a-zA-Z0-9\s&]+?)(?:\s+(?:and|we|I|it|with|for|to)\s|,|\.|!|\?|$)",
                r"(?:my company|our company)\s+(?:is\s+)?(?:called\s+)?([a-zA-Z0-9\s&]+?)(?:\s+(?:and|we|I|it|with)\s|,|\.|!|\?|$)"
            ]
            for pattern in company_patterns:
                company_match = re.search(pattern, user_text)
                if company_match:
                    company = sanitize_input(company_match.group(1).strip().title())
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
                sanitized_challenges = sanitize_input(user_message)
                await self.update_session_data(
                    session,
                    business_context={"challenges": sanitized_challenges}
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
                r"(?:under|less than|<)\s*\$?25k|\$?25,?000\b": "small (<$25k)",
                r"\$?25k\s*(?:to|-)\s*\$?100k|\$?25,?000\s*(?:to|-)\s*\$?100,?000|(?:^|[^1-9])\$?50k|(?:^|[^1-9])\$?50,?000\b|(?:^|[^1-9])\$?75k|(?:^|[^1-9])\$?75,?000\b": "medium ($25k-$100k)",
                r"(?:over|more than|>|>\s*)\$?100k|\$?100,?000\b|\$?150k|\$?150,?000\b|\$?200k|\$?200,?000\b": "large (>$100k)",
                r"\bsmall\b": "small (<$25k)",
                r"\bmedium\b": "medium ($25k-$100k)",
                r"\blarge\b": "large (>$100k)"
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
                r"\d+ months|next month|couple months|within \d+ months": "near-term (1-3 months)",
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
                r"(10-50|medium small|50 people|50 employees)": "10-50",
                r"(50-200|medium|100 people|100 employees)": "50-200",
                r"(200\+|200\s*(employees|people)|large|enterprise|1000|big)": "200+"
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

    async def _determine_next_phase(self, session: ConversationSession) -> SessionPhase | None:
        """Determine the next phase based on collected data.

        Returns the new phase if transition is needed, None otherwise.
        """
        from src.models.session import SessionPhase

        # Check what's missing in order of conversation flow
        current_phase = SessionPhase(session.current_phase)

        # Phase 1: Greeting - collect name
        if not session.client_info.get("name"):
            if current_phase != SessionPhase.GREETING:
                return SessionPhase.GREETING
            return None

        # Phase 2: Email collection
        if not session.client_info.get("email"):
            if current_phase != SessionPhase.DISCOVERY:
                return SessionPhase.DISCOVERY
            return None

        # Phase 3: Business challenge discovery
        if not session.business_context.get("challenges"):
            if current_phase != SessionPhase.DISCOVERY:
                return SessionPhase.DISCOVERY
            return None

        # Phase 4: Additional context (industry, company size)
        if (not session.business_context.get("industry") or
            not session.business_context.get("company_size")):
            if current_phase != SessionPhase.DISCOVERY:
                return SessionPhase.DISCOVERY
            return None

        # Phase 5: Qualification - Budget
        if not session.qualification.get("budget_range"):
            if current_phase != SessionPhase.QUALIFICATION:
                return SessionPhase.QUALIFICATION
            return None

        # Phase 6: Qualification - Timeline
        if not session.qualification.get("timeline"):
            if current_phase != SessionPhase.QUALIFICATION:
                return SessionPhase.QUALIFICATION
            return None

        # Phase 7: Service recommendation (if not already done)
        if not session.recommended_service:
            # Trigger service recommendation
            await self._recommend_service(session)
            # Move to PRD generation phase
            if current_phase != SessionPhase.PRD_GENERATION:
                return SessionPhase.PRD_GENERATION
            return None

        # Phase 8: PRD Generation
        if current_phase == SessionPhase.PRD_GENERATION and not session.prd_id:
            # Generate PRD
            await self._generate_prd_for_session(session)
            # Move to expert matching phase
            if current_phase != SessionPhase.EXPERT_MATCHING:
                return SessionPhase.EXPERT_MATCHING
            return None

        # All phases complete
        if current_phase != SessionPhase.EXPERT_MATCHING:
            return SessionPhase.EXPERT_MATCHING

        return None

    async def _generate_prd_for_session(self, session: ConversationSession) -> None:
        """Generate a PRD for the session."""
        from src.services.prd_service import PRDService

        # Use PRDService for consistent PRD generation
        prd_service = PRDService(self.db)
        await prd_service.generate_prd(session)

    async def match_experts_for_session(self, session: ConversationSession) -> list[dict[str, Any]]:
        """Match experts to a session based on business context and recommended service.

        Args:
            session: The conversation session

        Returns:
            List of matched experts with their scores and basic info
        """
        expert_service = ExpertService(self.db)

        # Get matching experts
        matched_experts = await expert_service.match_experts(
            service_type=session.recommended_service,
            business_context=session.business_context,
        )

        # Convert to serializable format
        results = []
        for expert, score in matched_experts:
            results.append({
                "id": str(expert.id),
                "name": expert.name,
                "email": expert.email,
                "role": expert.role,
                "bio": expert.bio,
                "photo_url": expert.photo_url,
                "specialties": expert.specialties,
                "services": expert.services,
                "match_score": round(score, 1),
            })

        # Update session with first matched expert if available
        if results and not session.matched_expert_id:
            try:
                import uuid
                session.matched_expert_id = uuid.UUID(results[0]["id"])
                self.db.add(session)
                await self.db.commit()
            except Exception:
                # If UUID conversion fails, just continue without updating
                pass

        return results

    async def _check_ambiguity(self, user_message: str, session: ConversationSession) -> dict:
        """Check if user response is ambiguous and needs clarification.

        Returns:
            Dict with is_ambiguous (bool) and reason (str) keys
        """
        import re
        user_text = user_message.lower().strip()

        # Check for very short responses first
        # (but exclude single word answers that are valid like names, emails)
        if len(user_text) < 5 and not re.search(r'@', user_text):
            # Single letter or very short non-name responses (2 chars or less)
            if len(user_text) < 2:
                return {"is_ambiguous": True, "reason": "too_short"}
            # 2-4 chars that are not valid names (contain numbers or symbols)
            if len(user_text) <= 4 and not re.search(r'^[a-z]+$', user_text):
                return {"is_ambiguous": True, "reason": "too_short"}

        # Check for specific ambiguity patterns with their reasons
        # Order matters - more specific patterns first
        patterns_with_reasons = [
            (r'^\s*(yes|no|yeah|nah|yep|nope)\s*$', "minimal_response"),
            (r'\b(not sure|not certain|don\'t know|don\'t really know|dunno)\b', "lack_of_knowledge"),
            (r'\b(i guess|i suppose|i think)\b', "guessing"),
            (r'\b(maybe|perhaps|possibly|probably|might|could)\b', "uncertainty"),
            (r'\b(whatever|anything|something|stuff|things)\b', "non_specific"),
            (r'\b(um|uh|er|ah|hmm|hum)\b', "hesitation"),
            (r'\b(sort of|kind of|kinda|sorta)\b', "uncertainty"),
        ]

        for pattern, reason in patterns_with_reasons:
            if re.search(pattern, user_text, re.IGNORECASE):
                return {"is_ambiguous": True, "reason": reason}

        # Check for responses that don't answer the specific question
        # Look at the last bot message to see what was asked
        last_messages = [msg for msg in session.messages if msg.role == MessageRole.ASSISTANT]
        if last_messages:
            last_bot_message = last_messages[-1].content.lower()

            # If bot asked for name and response doesn't contain name-like patterns
            if "name" in last_bot_message and not re.search(r'(name is|i am|i\'m|call me)', user_text):
                # But user provided something that looks like a name
                if len(user_text.split()) <= 3 and re.search(r'^[a-z\s]+$', user_text):
                    # This is actually fine, it's likely a name
                    return {"is_ambiguous": False, "reason": ""}

            # If bot asked for email and response doesn't contain @
            if "email" in last_bot_message and "@" not in user_text:
                # Check if it's a valid response to something else
                if not any(word in user_text for word in ["yes", "no", "maybe", "later"]):
                    return {"is_ambiguous": True, "reason": "missing_email_format"}

        return {"is_ambiguous": False, "reason": ""}

    def _generate_clarification_response(self, ambiguity_check: dict, user_message: str, session: ConversationSession) -> str:
        """Generate a clarification response based on the ambiguity type.

        Args:
            ambiguity_check: Dict with is_ambiguous and reason
            user_message: The ambiguous user message
            session: Current conversation session

        Returns:
            Clarification response text
        """
        reason = ambiguity_check["reason"]
        name = session.client_info.get("name", "there")

        # Get context about what we're asking
        clarification_messages = {
            "uncertainty": [
                f"I understand you're not completely sure, {name}. Could you help me understand a bit better?",
                "No problem if you're uncertain! Could you give me more details about what you're thinking?",
                f"That's totally fine, {name}. Could you tell me a bit more so I can help you better?"
            ],
            "lack_of_knowledge": [
                f"No worries at all, {name}! I'm here to help. Could you tell me what you do know about this?",
                "That's completely okay! Could you share any details you might have?",
                f"Thanks for being honest, {name}. Could you tell me more about your situation?"
            ],
            "guessing": [
                f"Thanks for sharing, {name}. Could you give me more specific details?",
                "I appreciate your input! Could you tell me more about what you're looking for?",
                f"Thanks for that, {name}. Could you provide a bit more detail?"
            ],
            "non_specific": [
                f"I'd love to help, {name}! Could you be more specific about what you're looking for?",
                "Thanks for sharing! Could you give me more details about what you need?",
                f"I understand, {name}. Could you tell me more specifically about your needs?"
            ],
            "minimal_response": [
                f"Thanks, {name}! Could you tell me a bit more about that?",
                "I appreciate your response! Could you elaborate a bit more?",
                f"Thanks for that, {name}. Could you give me more context?"
            ],
            "hesitation": [
                f"Take your time, {name}! I'm here to help whenever you're ready.",
                f"No rush, {name}. Could you tell me more when you're comfortable?",
                f"Whenever you're ready, {name}! I'd love to hear more details."
            ],
            "too_short": [
                f"Thanks, {name}! Could you give me a bit more detail?",
                "I appreciate your response! Could you elaborate a bit more?",
                f"Thanks for that, {name}. Could you tell me more?"
            ],
            "missing_email_format": [
                f"Thanks, {name}! Could you please provide your email address?",
                "I need your email to send you information. Could you share it with me?",
                "Could you provide your email address so I can follow up with you?"
            ]
        }

        # Get appropriate message or default
        messages = clarification_messages.get(reason, [
            f"Thanks, {name}! Could you give me more details about that?",
            f"I want to make sure I understand correctly, {name}. Could you tell me more?",
            "Thanks for sharing! Could you elaborate a bit more?"
        ])

        # Pick a random message from the options
        import random
        return random.choice(messages)

    async def _generate_streaming_response(
        self, user_message: str, conversation_history: list[dict], context: dict
    ) -> str:
        """Generate AI response using streaming for real-time updates."""
        full_response = ""

        # Use async iterator for streaming
        async for chunk in self.ai_service.stream_response(
            user_message, conversation_history, context
        ):
            full_response += chunk

        return full_response
