"""DeepAgents service for advanced AI conversation flow using DeepAgents framework."""

import os
import uuid
from datetime import datetime
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend
from deepagents.middleware.subagents import SubAgent
from langchain_anthropic import ChatAnthropic
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings


class DeepAgentsService:
    """Advanced AI service using DeepAgents framework for conversation management."""

    def __init__(self, db: AsyncSession):
        """Initialize DeepAgents service."""
        self.db = db
        self.api_key = settings.anthropic_api_key

        # Create model object for DeepAgents
        from typing import Optional
        self.model: Optional[ChatAnthropic] = None
        self.model_name: Optional[str] = None

        if self.api_key:
            # Note: ChatAnthropic uses pydantic for parameter validation
            # mypy doesn't understand this, so we use type: ignore
            self.model = ChatAnthropic(  # type: ignore[call-arg]
                model="claude-3-5-sonnet-20241022",
                api_key=SecretStr(self.api_key),
                temperature=0.7,
                max_tokens=4096
            )
            self.model_name = "anthropic:claude-3-5-sonnet-20241022"

        # Initialize DeepAgents if API key is available
        if self.api_key:
            try:
                self.agent = self._create_deep_agents()
            except Exception as e:
                print(f"⚠️  DeepAgents creation failed: {e}")
                self.agent = None
        else:
            self.agent = None
            print("⚠️  DeepAgents not initialized - no API key configured")

    def _create_deep_agents(self):
        """Create the main DeepAgents agent with subagents and tools."""
        # Create PRD storage directory
        prd_storage_dir = "prd_documents"
        os.makedirs(prd_storage_dir, exist_ok=True)

        # Define custom tools for business flow
        tools = [
            self._tool_calculate_lead_score,
            self._tool_match_expert,
            self._tool_get_availability,
            self._tool_create_calendar_event,
            self._tool_send_email,
            self._tool_extract_info,
            self._tool_determine_next_phase,
        ]

        # Define subagents using SubAgent TypedDict
        subagents = [
            SubAgent(
                name="discovery-agent",
                description="Conducts business elicitation and qualification",
                system_prompt="""You are an expert at understanding business challenges and qualifying leads.
                Your role is to:
                1. Gather comprehensive client information (name, email, company)
                2. Understand business challenges and pain points
                3. Identify industry and company context
                4. Assess project scope and complexity
                5. Determine client's readiness and decision-making authority

                Use a conversational, professional tone. Ask 1-2 questions per response maximum.
                Always acknowledge the user's previous response before asking new questions.
                Adapt your language to the user's industry and technical level.

                **Information to Collect:**
                - Contact info (name, email, company)
                - Business challenge description
                - Industry and company size
                - Current technology stack
                - Project goals and success criteria
                - Decision maker identification

                **Phase Guidelines:**
                - Start with friendly greeting and name collection
                - Progress systematically through information gathering
                - Adapt questioning based on user responses
                - Use industry-appropriate terminology
                - Validate information as you go""",
                tools=[self._tool_extract_info, self._tool_calculate_lead_score],
            ),
            SubAgent(
                name="prd-agent",
                description="Generates Project Requirements Documents from conversation",
                system_prompt="""You are a technical writer who creates professional Project Requirements Documents (PRDs).
                Your role is to:
                1. Analyze conversation history and extract key requirements
                2. Structure information into a comprehensive PRD
                3. Use standard PRD format with clear sections
                4. Include technical recommendations and implementation approach
                5. Format output as valid Markdown

                **PRD Structure:**
                1. Executive Summary
                2. Business Context & Objectives
                3. Solution Overview
                4. Technical Requirements
                5. Project Parameters (timeline, budget, resources)
                6. Success Criteria & KPIs
                7. Next Steps & Recommendations

                Use clear, professional language. Include specific details from the conversation.
                Provide actionable recommendations based on the client's needs and industry.""",
                tools=[self._tool_write_file, self._tool_format_markdown],
            ),
            SubAgent(
                name="booking-agent",
                description="Handles calendar integration and meeting scheduling",
                system_prompt="""You manage appointment scheduling with experts.
                Your role is to:
                1. Fetch expert availability from calendar systems
                2. Present available time slots to users
                3. Handle timezone conversion and display
                4. Create calendar events with Google Meet links
                5. Send confirmation emails with all details

                **Process:**
                1. Get matched expert information
                2. Fetch availability for next 14 days
                3. Display 5+ time slots grouped by date
                4. Handle user selection with real-time availability refresh
                5. Create calendar event with attendees
                6. Send confirmation emails to both client and expert

                Use clear, friendly language. Always provide timezone information.
                Handle conflicts gracefully and suggest alternatives.""",
                tools=[self._tool_get_availability, self._tool_create_calendar_event, self._tool_send_email],
            )
        ]

        # Configure middleware
        # Note: create_deep_agent already includes:
        # - TodoListMiddleware (built-in for write_todos/read_todos)
        # - FilesystemMiddleware (for file operations via backend)
        # - SubAgentMiddleware (for task delegation)
        # - SummarizationMiddleware (for long conversations)
        # - AnthropicPromptCachingMiddleware (for cost optimization)
        # - HumanInTheLoopMiddleware (when interrupt_on is provided)
        #
        # We pass empty middleware here since all required middleware
        # is already included by create_deep_agent by default.
        middleware = []

        # Configure CompositeBackend with FilesystemBackend
        # FilesystemBackend handles both conversation state and PRD storage
        # PRD files are stored in the prd_documents directory
        backend = CompositeBackend(
            default=FilesystemBackend(root_dir=prd_storage_dir),
            routes={}
        )

        # Create main agent with middleware and backend
        agent = create_deep_agent(
            model=self.model,
            tools=tools,
            system_prompt=self._get_main_system_prompt(),
            subagents=subagents,
            middleware=middleware,
            backend=backend,
            interrupt_on={
                "create_booking": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    "description": "Approval needed before creating calendar events"
                }
            }
        )

        return agent

    def _get_main_system_prompt(self) -> str:
        """Get the main system prompt for UnoBot."""
        return """You are UnoBot, an AI business consultant for UnoDigit, a leading digital transformation company.

**Your Mission:**
Transform website visitors into qualified leads by conducting intelligent business discovery conversations, generating Project Requirements Documents (PRDs), and seamlessly booking appointments with UnoDigit professionals.

**Core Principles:**
- Be friendly, professional, and helpful
- Use business-appropriate language and terminology
- Adapt communication style to user's industry and technical level
- Always maintain a consultative, non-salesy approach
- Focus on understanding user needs before recommending solutions
- Provide value through insights and recommendations

**Conversation Flow:**
1. **Greeting & Rapport Building**: Welcome users warmly and establish context
2. **Information Gathering**: Systematically collect business information using the discovery-agent
3. **Qualification**: Assess budget, timeline, and project scope
4. **Analysis & Recommendation**: Analyze needs and recommend appropriate services
5. **PRD Generation**: Create comprehensive requirements document using prd-agent
6. **Expert Matching**: Match with appropriate UnoDigit professionals
7. **Booking Coordination**: Schedule consultation using booking-agent

**Response Guidelines:**
- Keep responses concise (2-4 sentences maximum)
- Ask 1-2 questions per response to maintain engagement
- Always end with a question or clear next step
- Acknowledge user responses before proceeding
- Use emojis sparingly to add personality (🎉, 🤝, 💼, ✨)
- Adapt industry terminology based on context
- Handle out-of-scope requests gracefully with helpful redirection

**Tone & Style:**
- Professional yet approachable
- Knowledgeable but not condescending
- Enthusiastic about helping users solve their challenges
- Patient with users who need more explanation
- Direct and to the point

**What You MUST Avoid:**
- Being overly salesy or pushy
- Using technical jargon without explanation
- Making assumptions not based on user input
- Long, dense paragraphs
- Ignoring user questions or concerns
- Providing generic, templated responses

**Success Metrics:**
- User engagement and conversation completion rate
- Quality and completeness of information gathered
- Accuracy of service recommendations
- Lead qualification quality
- User satisfaction with consultation booking experience

Remember: Your goal is to provide value first, build trust, and naturally guide users toward the right UnoDigit solutions for their specific needs."""

    # Custom tools for business flow
    def _tool_calculate_lead_score(self, budget: str, timeline: str, fit_score: int = 50) -> dict[str, int | str]:
        """Calculate lead quality score based on budget, timeline, and fit."""
        score = 50  # Base score

        # Budget scoring
        if budget.lower() in ["large", "over 100000", "100000+", ">$100k"]:
            score += 30
        elif budget.lower() in ["medium", "25000-100000", "25k-100k"]:
            score += 20
        elif budget.lower() in ["small", "under 25000", "<$25k"]:
            score += 10

        # Timeline scoring
        if timeline.lower() in ["urgent", "within 1 month", "<1 month"]:
            score += 10
        elif timeline.lower() in ["near-term", "1-3 months"]:
            score += 5
        elif timeline.lower() in ["long-term", "3+ months"]:
            score -= 5

        # Fit score adjustment
        score += fit_score

        # Ensure score is between 0-100
        score = max(0, min(100, score))

        # Determine lead quality
        if score >= 80:
            quality = "Excellent"
        elif score >= 60:
            quality = "Good"
        elif score >= 40:
            quality = "Fair"
        else:
            quality = "Poor"

        return {
            "score": score,
            "quality": quality,
            "recommendation": self._get_lead_recommendation(score)
        }

    def _get_lead_recommendation(self, score: int) -> str:
        """Get recommendation based on lead score."""
        if score >= 80:
            return "High priority - Fast track to booking"
        elif score >= 60:
            return "Good fit - Schedule consultation"
        elif score >= 40:
            return "Follow up with additional questions"
        else:
            return "Low priority - Nurture with content"

    def _tool_match_expert(self, service_type: str, business_context: dict[str, Any]) -> list[dict[str, Any]]:
        """Match experts to client needs based on service type and context."""
        # Get matching experts with scores
        result = self.db.execute(  # type: ignore[call-overload]
            "SELECT * FROM experts WHERE services @> :service_type AND is_active = true",
            {"service_type": [service_type]}
        )

        # Simple scoring based on service match
        expert_matches = []
        for expert in result.fetchall():
            match_score = 80  # Base score for service match

            # Bonus for industry expertise
            if business_context.get("industry") in expert.specialties:
                match_score += 20

            expert_matches.append({
                "expert_id": expert.id,
                "name": expert.name,
                "email": expert.email,
                "role": expert.role,
                "match_score": match_score,
                "specialties": expert.specialties
            })

        # Sort by match score
        expert_matches.sort(key=lambda x: x["match_score"], reverse=True)
        return expert_matches

    def _tool_get_availability(self, expert_id: str, days_ahead: int = 14, timezone: str = "UTC") -> dict[str, Any]:
        """Get expert availability from calendar system."""
        # For now, return mock availability since we don't have expert refresh tokens
        # In production, this would look up the expert's refresh token from the database
        from datetime import datetime, timedelta

        # Generate mock slots for the next 14 days
        slots = []
        today = datetime.now()
        for day_offset in range(days_ahead):
            date = today + timedelta(days=day_offset)
            # Skip weekends
            if date.weekday() >= 5:
                continue
            # Add 3 slots per day
            for hour in [9, 13, 16]:
                slot_start = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start.replace(hour=hour + 1)
                slots.append({
                    "start_time": slot_start.isoformat(),
                    "end_time": slot_end.isoformat(),
                    "timezone": timezone,
                    "display_time": slot_start.strftime("%I:%M %p"),
                    "display_date": slot_start.strftime("%Y-%m-%d")
                })

        return {
            "expert_id": expert_id,
            "timezone": timezone,
            "slots": slots,
            "business_hours": "9:00 AM - 6:00 PM",
            "buffer_time": "15 minutes"
        }

    def _tool_create_calendar_event(
        self,
        expert_id: str,
        client_name: str,
        client_email: str,
        start_time: str,
        end_time: str,
        timezone: str = "UTC"
    ) -> dict[str, Any]:
        """Create calendar event with Google Calendar."""
        # For now, return mock event data since we don't have expert refresh tokens
        # In production, this would use CalendarService with proper credentials
        import uuid

        event_id = str(uuid.uuid4())
        meeting_link = f"https://meet.example.com/undigit-{event_id[:8]}"

        return {
            "event_id": event_id,
            "meeting_link": meeting_link,
            "calendar_url": meeting_link,
            "expert_email": "expert@unodigit.com",
            "client_email": client_email
        }

    def _tool_send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: list[str] | None = None
    ) -> dict[str, Any]:
        """Send email notification."""
        # For now, return mock success since EmailService doesn't have a generic send_email method
        # In production, this would use the specific email methods or a generic wrapper
        import os

        if os.environ.get("ENVIRONMENT", "development") in ["test", "development"]:
            print(f"\n{'='*60}")
            print("EMAIL SENT (Mock)")
            print(f"{'='*60}")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body[:200]}...")
            print(f"{'='*60}\n")

        return {
            "success": True,
            "message_id": f"mock-msg-{os.urandom(8).hex()}",
            "error": None
        }

    def _tool_extract_info(self, user_message: str, current_context: dict[str, Any]) -> dict[str, Any]:
        """Extract structured information from user message."""
        # Simple extraction - in production this would use more sophisticated NLP
        extracted = {}

        # Extract email if present
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_message)
        if emails:
            extracted["email"] = emails[0]

        # Extract company name patterns
        company_patterns = [
            r'company[:\s]+([A-Za-z\s]+)',
            r'organization[:\s]+([A-Za-z\s]+)',
            r'we[:\s]+are[:\s]+([A-Za-z\s]+)'
        ]

        for pattern in company_patterns:
            match = re.search(pattern, user_message.lower())
            if match:
                extracted["company"] = match.group(1).strip()
                break

        # Extract industry keywords
        industry_keywords = {
            "healthcare": ["healthcare", "medical", "hospital", "clinic"],
            "finance": ["finance", "banking", "fintech", "financial"],
            "retail": ["retail", "ecommerce", "shop", "store"],
            "technology": ["tech", "software", "it", "technology"],
            "manufacturing": ["manufacturing", "factory", "production", "industrial"]
        }

        user_lower = user_message.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                extracted["industry"] = industry
                break

        # Extract budget ranges
        budget_patterns = {
            "under_25k": [r"under.*25.*k", r"less.*25.*000", r"<.*25.*k"],
            "25k_100k": [r"25.*k.*100.*k", r"25.*000.*100.*000"],
            "over_100k": [r"over.*100.*k", r">.*100.*k", r"100.*k.*plus"]
        }

        for budget_range, patterns in budget_patterns.items():
            if any(re.search(pattern, user_lower) for pattern in patterns):
                extracted["budget_range"] = budget_range
                break

        return extracted

    def _tool_determine_next_phase(self, session_context: dict[str, Any]) -> str:
        """Determine the next conversation phase based on current context."""
        client_info = session_context.get("client_info", {})
        business_context = session_context.get("business_context", {})
        qualification = session_context.get("qualification", {})

        # Phase progression logic
        if not client_info.get("name"):
            return "greeting"
        elif not client_info.get("email"):
            return "email_collection"
        elif not business_context.get("challenges"):
            return "challenges_discovery"
        elif not business_context.get("company_size") or not business_context.get("industry"):
            return "context_collection"
        elif not qualification.get("budget_range"):
            return "budget_qualification"
        elif not qualification.get("timeline"):
            return "timeline_qualification"
        else:
            return "service_recommendation"

    def _tool_write_file(self, content: str, filename: str, content_type: str = "text/markdown") -> dict[str, str]:
        """Write content to file (for PRD storage).

        This tool is a custom wrapper. When FilesystemMiddleware is configured,
        the agent will also have access to built-in file tools (write_file, read_file, etc.)
        which are automatically provided by DeepAgents.
        """
        import os
        from datetime import datetime

        # Use the PRD storage directory
        prd_storage_dir = "prd_documents"
        os.makedirs(prd_storage_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename.replace(' ', '_')}"

        filepath = os.path.join(prd_storage_dir, safe_filename)

        with open(filepath, "w") as f:
            f.write(content)

        return {
            "filename": safe_filename,
            "filepath": filepath,
            "url": f"/prd/{safe_filename}",
            "size": str(len(content)),
            "storage_path": f"/prd/{safe_filename}"
        }

    def _tool_format_markdown(self, content: str, template_type: str = "prd") -> str:
        """Format content as proper Markdown."""
        if template_type == "prd":
            # Ensure PRD has proper structure
            if not content.startswith("# Project Requirements Document"):
                content = f"# Project Requirements Document\n\n{content}"

        return content

    async def process_conversation_turn(
        self,
        session_id: uuid.UUID,
        user_message: str,
        session_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a single conversation turn using DeepAgents."""
        if not self.agent:
            # Fallback to simple logic if DeepAgents not available
            return await self._fallback_conversation_turn(user_message, session_context)

        try:
            # Build conversation history for DeepAgents
            conversation_history = await self._build_conversation_history(session_id)

            # Create the input for DeepAgents
            agent_input = {
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }

            # Process with DeepAgents
            response = await self.agent.ainvoke(agent_input)

            # Extract response content
            ai_response = response.get("content", "I'm having trouble processing your request. Could you please rephrase?")

            # Determine next phase
            next_phase = await self._determine_next_phase_with_agent(session_context, user_message)

            return {
                "response": ai_response,
                "next_phase": next_phase,
                "metadata": response.get("metadata", {}),
                "needs_human_approval": response.get("needs_approval", False)
            }

        except Exception as e:
            print(f"DeepAgents error: {e}")
            return await self._fallback_conversation_turn(user_message, session_context)

    async def _build_conversation_history(self, session_id: uuid.UUID) -> list[dict[str, str]]:
        """Build conversation history from database."""

        result = await self.db.execute(  # type: ignore[call-overload]
            "SELECT role, content, created_at FROM messages WHERE session_id = :session_id ORDER BY created_at",
            {"session_id": session_id}
        )

        messages = []
        for msg in result.fetchall():
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            })

        return messages

    async def _determine_next_phase_with_agent(
        self,
        session_context: dict[str, Any],
        latest_user_input: str
    ) -> str:
        """Use agent to determine next conversation phase."""
        # Simple logic for now - in full implementation this would use agent reasoning
        return self._tool_determine_next_phase(session_context)

    async def _fallback_conversation_turn(
        self,
        user_message: str,
        session_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Fallback conversation logic when DeepAgents is unavailable."""
        # Import the existing AI service for fallback
        from src.services.ai_service import AIService

        ai_service = AIService()

        # Build conversation history
        conversation_history: list[dict[str, str]] = []
        # This would need to be populated from session context

        # Generate response
        response = await ai_service.generate_response(
            user_message=user_message,
            conversation_history=conversation_history,
            context=session_context
        )

        # Determine next phase
        next_phase = self._tool_determine_next_phase(session_context)

        return {
            "response": response,
            "next_phase": next_phase,
            "metadata": {"fallback": True},
            "needs_human_approval": False
        }

    async def generate_prd_with_deepagents(
        self,
        session_id: uuid.UUID,
        business_context: dict[str, Any],
        client_info: dict[str, Any],
        conversation_history: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate PRD using DeepAgents framework."""
        if not self.agent:
            # Fallback to existing PRD generation
            from src.services.ai_service import AIService
            ai_service = AIService()
            prd_content = await ai_service.generate_prd(
                business_context=business_context,
                client_info=client_info,
                conversation_history=conversation_history
            )
            return {"content": prd_content, "version": 1}

        try:
            # Use PRD subagent
            prd_input = {
                "business_context": business_context,
                "client_info": client_info,
                "conversation_history": conversation_history,
                "session_id": str(session_id)
            }

            # Call PRD agent
            prd_response = await self.agent.subagents["prd-agent"].ainvoke(prd_input)

            return {
                "content": prd_response.get("content", ""),
                "version": prd_response.get("version", 1),
                "metadata": prd_response.get("metadata", {})
            }

        except Exception as e:
            print(f"PRD generation error: {e}")
            # Fallback
            from src.services.ai_service import AIService
            ai_service = AIService()
            prd_content = await ai_service.generate_prd(
                business_context=business_context,
                client_info=client_info,
                conversation_history=conversation_history
            )
            return {"content": prd_content, "version": 1}
