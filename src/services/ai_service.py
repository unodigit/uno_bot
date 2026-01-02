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

Your role is to:
1. Greet visitors warmly and understand their business needs
2. Ask qualifying questions to understand their challenges
3. Recommend appropriate UnoDigit services
4. Guide them toward booking a consultation

UnoDigit Services:
- AI Strategy & Planning
- Custom Software Development
- Data Intelligence & Analytics
- Cloud Infrastructure & DevOps
- Digital Transformation Consulting

Key capabilities:
- Conduct business discovery conversations
- Qualify leads based on budget, timeline, and needs
- Match clients with appropriate experts
- Generate Project Requirements Documents (PRDs)
- Schedule appointments with experts

Guidelines:
- Be conversational and friendly, not robotic
- Ask 2-3 questions at a time to avoid overwhelming
- Listen to the user's needs before recommending
- Keep responses concise and focused
- Use business terminology appropriately
- End responses with questions to continue conversation

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
        user_message_lower = user_message.lower()

        if any(greeting in user_message_lower for greeting in ["hi", "hello", "hey"]):
            return "Hello! 👋 Welcome to UnoDigit. I'm here to help you explore how we can transform your business with AI-powered solutions. What brings you here today?"

        if any(word in user_message_lower for word in ["help", "service", "what do you do"]):
            return "I can help you with:\n\n• AI Strategy & Planning\n• Custom Software Development\n• Data Intelligence Solutions\n• Cloud Infrastructure\n\nWhat specific challenge are you facing?"

        if any(word in user_message_lower for word in ["ai", "machine learning", "intelligence"]):
            return "Great! AI is our specialty. We help businesses implement:\n\n• Predictive analytics\n• Process automation\n• Custom ML models\n• AI strategy & roadmap\n\nWhat kind of AI solution are you considering?"

        if any(word in user_message_lower for word in ["price", "cost", "budget"]):
            return "Every project is custom, so pricing depends on scope and complexity. Typical projects range from $10k for focused solutions to $100k+ for enterprise transformations. Let's discuss your needs first - what's the problem you're trying to solve?"

        if any(word in user_message_lower for word in ["book", "meeting", "call", "appointment"]):
            return "I'd be happy to help you book a consultation! To find the best time, could you share:\n\n1. Your preferred time zone\n2. 2-3 time slots that work for you\n3. What you'd like to discuss\n\nI'll match you with the right expert."

        return "Thank you for your message! I'm processing your request. To help you best, could you tell me more about what you're looking for?"

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
