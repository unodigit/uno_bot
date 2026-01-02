"""AI service for generating responses using LangChain/DeepAgents."""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.core.config import settings


class AIService:
    """Service for AI-powered conversation responses."""

    def __init__(self):
        """Initialize the AI service with Anthropic Claude."""
        self.api_key = settings.anthropic_api_key
        self.model_name = settings.anthropic_model

        if not self.api_key:
            # For demo/testing without API key
            self.llm = None
        else:
            self.llm = ChatAnthropic(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=1024,
            )

    async def generate_response(
        self,
        user_message: str,
        conversation_history: list[dict] = None,
        context: dict = None,
    ) -> str:
        """Generate an AI response to a user message.

        Args:
            user_message: The user's message
            conversation_history: List of previous messages with role/content
            context: Additional context about the session

        Returns:
            AI-generated response text
        """
        if not self.llm:
            # Fallback response when no API key is configured
            return self._fallback_response(user_message, context)

        # Build prompt with conversation history
        messages = [
            SystemMessage(content=self._get_system_prompt(context)),
        ]

        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=user_message))

        try:
            # Generate response
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"AI service error: {e}")
            return self._fallback_response(user_message, context)

    def _get_system_prompt(self, context: dict | None) -> str:
        """Get the system prompt for the AI assistant."""
        base_prompt = """You are UnoBot, an AI business consultant for UnoDigit, a digital transformation company.

Your role is to conduct a structured business discovery conversation:

**Conversation Phases:**
1. **Greeting & Name Collection**: Ask for user's name and introduce yourself
2. **Email Collection**: Collect and validate email address for follow-up
3. **Business Challenge Discovery**: Ask about current challenges and pain points
4. **Qualification**: Understand budget, timeline, and decision-making process
5. **Service Recommendation**: Recommend appropriate UnoDigit services
6. **Expert Matching**: Match with appropriate expert and show availability
7. **Booking**: Help book appointment with expert

**Current Phase Detection:**
- If no client_info.name: ASK FOR NAME
- If no client_info.email: ASK FOR EMAIL
- If no business_context.challenges: ASK ABOUT CHALLENGES
- If no qualification.budget_range: ASK ABOUT BUDGET
- If no qualification.timeline: ASK ABOUT TIMELINE
- Otherwise: RECOMMEND SERVICES AND BOOK APPOINTMENT

**Phase 1 - Name Collection:**
- Ask: "What's your name?"
- Be friendly and professional
- Use their name in subsequent responses

**Phase 2 - Email Collection:**
- Ask for email address
- Validate email format
- Explain why email is needed (for follow-up and PRD)

**Phase 3 - Business Challenge Discovery:**
- Ask about current business challenges
- Ask about industry and company size
- Ask about technology stack
- Ask about goals and objectives

**Phase 4 - Qualification:**
- Ask about budget range (small <$25k, medium $25k-$100k, large >$100k)
- Ask about project timeline (urgent <1 month, near-term 1-3 months, long-term 3+ months)
- Ask if they are the decision maker

**Guidelines:**
- Ask 2-3 questions at a time to avoid overwhelming
- Always ask for ONE piece of information at a time
- Listen to the user's needs before recommending
- Keep responses concise and focused
- Use business terminology appropriately
- End responses with questions to continue conversation

UnoDigit Services:
- AI Strategy & Planning
- Custom Software Development
- Data Intelligence & Analytics
- Cloud Infrastructure & DevOps
- Digital Transformation Consulting

Current context:
"""
        if context:
            if context.get("business_context"):
                base_prompt += f"\nBusiness Context: {context['business_context']}"
            if context.get("client_info"):
                base_prompt += f"\nClient Info: {context['client_info']}"

        return base_prompt

    def _fallback_response(self, user_message: str, context: dict | None) -> str:
        """Generate a fallback response when AI service is unavailable."""
        # Initialize context if not provided
        if context is None:
            context = {"client_info": {}, "business_context": {}, "qualification": {}}

        client_info = context.get("client_info", {})
        business_context = context.get("business_context", {})
        qualification = context.get("qualification", {})

        # Phase 1: Name Collection
        if not client_info.get("name"):
            return """🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.

Before we dive into your business needs, what's your name? I'd love to address you personally!"""

        # Phase 2: Email Collection
        if not client_info.get("email"):
            return f"""Nice to meet you, {client_info.get('name', 'there')}! 🤝

To help you best and send you a personalized proposal, I'll need your email address. This will also be used to share your custom Project Requirements Document once we understand your needs better.

What's the best email to reach you at?"""

        # Phase 3: Business Challenge Discovery
        if not business_context.get("challenges"):
            return f"""Perfect! Thanks for sharing that, {client_info.get('name')}! ✨

Now, let's talk about your business. To help you best, I'd love to understand:

1. **What's the main business challenge** you're looking to solve with technology?
2. **What industry** are you in?
3. **How many people** are in your organization?

This helps me match you with the right solutions!"""

    async def generate_prd(
        self,
        business_context: dict,
        client_info: dict,
        conversation_history: list[dict],
    ) -> str:
        """Generate a Project Requirements Document."""
        if not self.llm:
            return self._fallback_prd(business_context, client_info)

        prompt = f"""Generate a detailed Project Requirements Document (PRD) for a digital transformation project.

Client Information:
{client_info}

Business Context:
{business_context}

Conversation History:
{conversation_history}

Please generate a comprehensive PRD including:
1. Executive Summary
2. Business Objectives
3. Technical Requirements
4. Scope & Deliverables
5. Timeline & Milestones
6. Success Criteria
7. Recommended Approach

Format the response in clear Markdown.
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert technical product manager. Generate detailed PRDs."),
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception:
            return self._fallback_prd(business_context, client_info)

    def _fallback_prd(self, business_context: dict, client_info: dict) -> str:
        """Fallback PRD when AI service is unavailable."""
        company = client_info.get("company", "Client")
        industry = business_context.get("industry", "technology")

        return f"""# Project Requirements Document

## Executive Summary
This PRD outlines the requirements for a digital transformation project for {company} in the {industry} sector.

## Business Objectives
- Modernize existing systems and processes
- Improve operational efficiency
- Enable data-driven decision making
- Enhance customer experience

## Technical Requirements
- Modern web application architecture
- Cloud-native deployment
- Scalable database solution
- Real-time data processing
- Secure authentication & authorization

## Scope & Deliverables
1. Discovery & Planning Phase
2. System Architecture Design
3. Core Application Development
4. Data Integration & Migration
5. Testing & Quality Assurance
6. Deployment & Training

## Timeline & Milestones
- Phase 1 (Weeks 1-4): Discovery & Design
- Phase 2 (Weeks 5-12): Development
- Phase 3 (Weeks 13-16): Testing & Deployment

## Success Criteria
- 50% reduction in manual processes
- 99.9% system uptime
- Sub-second response times
- Positive user feedback

## Recommended Approach
We recommend an agile methodology with bi-weekly sprints and regular stakeholder reviews.
"""
