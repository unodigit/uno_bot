"""AI service for generating responses using LangChain/DeepAgents."""
import asyncio
from typing import Any, AsyncIterator, Optional, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage

from src.core.config import settings


class AIService:
    """Service for AI-powered conversation responses."""

    def __init__(self) -> None:
        """Initialize the AI service with Anthropic Claude."""
        self.api_key = settings.anthropic_api_key
        self.model_name = settings.anthropic_model

        if not self.api_key:
            # For demo/testing without API key
            self.llm: Optional[ChatAnthropic] = None
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
        conversation_history: Optional[list[dict[str, Any]]] = None,
        context: Optional[dict[str, Any]] = None,
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
        messages: list[BaseMessage] = [
            SystemMessage(content=self._get_system_prompt(context)),
        ]

        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=user_message))

        try:
            # Generate response
            response = await self.llm.ainvoke(messages)
            return cast(str, response.content)
        except Exception as e:
            print(f"AI service error: {e}")
            return self._fallback_response(user_message, context)

    async def stream_response(
        self,
        user_message: str,
        conversation_history: Optional[list[dict[str, Any]]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Stream AI response chunks for real-time updates.

        Args:
            user_message: The user's message
            conversation_history: List of previous messages with role/content
            context: Additional context about the session

        Yields:
            Response chunks as they become available
        """
        if not self.llm:
            # Fallback - return chunks for demo
            response = self._fallback_response(user_message, context)
            for i in range(0, len(response), 10):
                yield response[i:i+10]
                await asyncio.sleep(0.05)  # Small delay for demo
            return

        # Build prompt with conversation history
        messages: list[BaseMessage] = [
            SystemMessage(content=self._get_system_prompt(context)),
        ]

        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=user_message))

        try:
            # Stream response chunks
            async for chunk in self.llm.astream(messages):
                yield cast(str, chunk.content)
        except Exception as e:
            print(f"AI streaming error: {e}")
            fallback = self._fallback_response(user_message, context)
            for i in range(0, len(fallback), 10):
                yield fallback[i:i+10]
                await asyncio.sleep(0.05)

    def _get_system_prompt(self, context: Optional[dict[str, Any]]) -> str:
        """Get the system prompt for the AI assistant."""
        base_prompt = """You are UnoBot, an AI business consultant for UnoDigit, a digital transformation company.

Your role is to conduct a structured business discovery conversation to qualify leads and collect information for Project Requirements Documents (PRDs).

**Conversation Phases (in order):**
1. **Greeting & Name Collection**: Ask for user's name
2. **Email Collection**: Collect and validate email address
3. **Business Challenge Discovery**: Ask about challenges, industry, company name
4. **Company Context**: Ask about company size and technology stack
5. **Qualification - Budget**: Ask about budget range
6. **Qualification - Timeline**: Ask about project timeline
7. **Service Recommendation**: Recommend appropriate services based on collected info

**Detailed Phase Instructions:**

**Phase 1 - Name Collection:**
- Ask: "What's your name?"
- Be friendly and professional
- Use their name in subsequent responses

**Phase 2 - Email Collection:**
- Ask: "What's your email address?"
- Explain: "I'll use this to send your PRD and follow up"
- Validate format (basic)

**Phase 3 - Business Challenge Discovery:**
- Ask about main business challenges/pain points
- Ask about industry (healthcare, finance, retail, tech, etc.)
- Ask about company name
- Be conversational: "Tell me about the challenges you're facing"

**Phase 4 - Company Context:**
- Ask about company size: "How large is your team?"
- Ask about current tech stack if relevant
- Options: startup, 10-50, 50-200, 200+

**Phase 5 - Budget Qualification:**
- Ask: "What's your approximate budget range?"
- Provide options:
  • Small: Under $25,000
  • Medium: $25,000 - $100,000
  • Large: Over $100,000

**Phase 6 - Timeline Qualification:**
- Ask: "What's your timeline for this project?"
- Provide options:
  • Urgent: Within 1 month
  • Near-term: 1-3 months
  • Long-term: 3+ months

**Phase 7 - Service Recommendation:**
- Based on all collected info, recommend appropriate service
- AI Strategy & Planning: For AI/ML/data needs
- Custom Software Development: For app/website development
- Data Intelligence & Analytics: For data/analytics needs
- Cloud Infrastructure & DevOps: For cloud/infrastructure needs
- Digital Transformation Consulting: For strategy/consulting

**Response Guidelines:**
- Keep responses concise (2-4 sentences)
- Ask 1-2 questions max per response
- Always end with a question to continue conversation
- Use business terminology appropriately
- Be helpful and professional
- Acknowledge user's responses

**Out-of-Scope Request Handling:**
- If user asks about unrelated topics (weather, news, sports, personal advice, etc.):
  1. Politely acknowledge the question
  2. Gently redirect back to business consulting
  3. Offer to help with their business needs
  4. Example: "I appreciate your interest, but I'm focused on helping businesses with digital transformation. Let's get back to understanding your business challenges - what industry are you in?"

**Industry-Specific Terminology:**
- Adapt your language based on the user's industry:
  - **Healthcare**: Use terms like "patient data," "HIPAA compliance," "clinical workflows," "healthcare systems"
  - **Finance**: Use terms like "financial data," "compliance," "risk management," "transaction processing"
  - **Retail/E-commerce**: Use terms like "customer experience," "inventory management," "conversion rates," "omnichannel"
  - **Manufacturing**: Use terms like "supply chain," "operational efficiency," "IoT," "automation"
  - **Technology/SaaS**: Use terms like "scalability," "APIs," "cloud infrastructure," "user acquisition"
  - **General/Other**: Use standard business terminology

**Example Flow:**
User: "Hi, I need help"
Bot: "🎉 Welcome! I'm UnoBot from UnoDigit. What's your name?"

User: "I'm John"
Bot: "Nice to meet you, John! What's your email address?"

User: "john@example.com"
Bot: "Thanks, John! What business challenge are you looking to solve?"

User: "We need to improve our data analytics"
Bot: "Great! What industry are you in, and what's your company name?"

Current context:
"""
        if context:
            if context.get("business_context"):
                base_prompt += f"\nBusiness Context: {context['business_context']}"
            if context.get("client_info"):
                base_prompt += f"\nClient Info: {context['client_info']}"

        return base_prompt

    def _fallback_response(self, user_message: str, context: Optional[dict[str, Any]]) -> str:
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
3. **What's your company name?**

This helps me match you with the right solutions!"""

        # Phase 4: Additional Context (Company size, tech stack)
        if not business_context.get("company_size") or not business_context.get("industry"):
            response = f"""Great! Thanks for sharing about your challenges, {client_info.get('name')}.\n\n"""
            if not business_context.get("industry"):
                response += "What industry are you in? (e.g., healthcare, finance, retail, tech)\n\n"
            if not business_context.get("company_size"):
                response += "How large is your organization? (e.g., startup, 10-50 people, 50-200, enterprise)"
            return response

        # Phase 5: Qualification - Budget
        if not qualification.get("budget_range"):
            return f"""Thanks for the context, {client_info.get('name')}! 💼\n\nTo help me recommend the right solution, what's your approximate budget range?\n\n• Small: Under $25,000\n• Medium: $25,000 - $100,000\n• Large: Over $100,000"""

        # Phase 6: Qualification - Timeline
        if not qualification.get("timeline"):
            return """Perfect! And what's your timeline for this project?\n\n• Urgent: Within 1 month\n• Near-term: 1-3 months\n• Long-term: 3+ months"""

        # Phase 7: Service Recommendation
        return f"""Excellent! I've gathered all the information I need. Based on your needs, I recommend:\n\n**{business_context.get('industry', 'Your')} Industry Solutions**\n\nLet me connect you with one of our experts who specializes in this area. Would you like to see available appointment times?"""

    async def generate_prd(
        self,
        business_context: dict[str, Any],
        client_info: dict[str, Any],
        conversation_history: list[dict[str, Any]],
        feedback: Optional[str] = None,
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
{conversation_history}"""

        if feedback:
            prompt += f"\n\nFeedback for this version:\n{feedback}\n\nPlease incorporate this feedback into the updated PRD."

        prompt += """
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
            return cast(str, response.content)
        except Exception:
            return self._fallback_prd(business_context, client_info)

    def _fallback_prd(self, business_context: dict[str, Any], client_info: dict[str, Any]) -> str:
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
