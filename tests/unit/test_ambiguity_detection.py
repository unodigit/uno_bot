"""Unit tests for ambiguity detection in session service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.services.session_service import SessionService
from src.models.session import ConversationSession, MessageRole


class TestAmbiguityDetection:
    """Test cases for ambiguity detection functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        return db

    @pytest.fixture
    def session_service(self, mock_db):
        """Create a session service with mocked dependencies."""
        service = SessionService(mock_db)
        # Mock the AI service to avoid API calls
        service.ai_service = MagicMock()
        service.ai_service.generate_response = AsyncMock(return_value="Mock response")
        return service

    @pytest.fixture
    def sample_session(self):
        """Create a sample conversation session."""
        session = ConversationSession(
            id="12345678-1234-1234-1234-123456789012",
            visitor_id="test-visitor",
            status="active",
            current_phase="greeting",
            client_info={"name": "Test User"},
            business_context={},
            qualification={},
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        # Mock messages relationship
        session.messages = []
        return session

    @pytest.mark.asyncio
    async def test_detects_uncertainty_keywords(self, session_service, sample_session):
        """Test that uncertainty keywords are detected."""
        ambiguous_messages = [
            "maybe",
            "perhaps",
            "possibly",
            "probably",
            "might be",
            "could be",
            "sort of",
            "kind of",
            "kinda",
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "uncertainty"

    @pytest.mark.asyncio
    async def test_detects_lack_of_knowledge(self, session_service, sample_session):
        """Test that lack of knowledge indicators are detected."""
        ambiguous_messages = [
            "not sure",
            "not certain",
            "don't know",
            "don't really know",
            "dunno",
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "lack_of_knowledge"

    @pytest.mark.asyncio
    async def test_detects_guessing_responses(self, session_service, sample_session):
        """Test that guessing responses are detected."""
        ambiguous_messages = [
            "i guess",
            "i suppose",
            "i think",
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "guessing"

    @pytest.mark.asyncio
    async def test_detects_non_specific_responses(self, session_service, sample_session):
        """Test that non-specific responses are detected."""
        ambiguous_messages = [
            "whatever",
            "anything",
            "something",
            "stuff",
            "things",
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "non_specific"

    @pytest.mark.asyncio
    async def test_detects_minimal_responses(self, session_service, sample_session):
        """Test that minimal yes/no responses are detected."""
        ambiguous_messages = [
            "yes",
            "no",
            "yeah",
            "nah",
            "yep",
            "nope",
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "minimal_response"

    @pytest.mark.asyncio
    async def test_detects_hesitation_sounds(self, session_service, sample_session):
        """Test that hesitation sounds are detected."""
        ambiguous_messages = [
            "um",
            "uh",
            "er",
            "ah",
            "hmm",
            "hum",
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "hesitation"

    @pytest.mark.asyncio
    async def test_detects_too_short_responses(self, session_service, sample_session):
        """Test that very short responses are detected."""
        ambiguous_messages = [
            "a",      # 1 char
            "123",    # 3 chars with numbers
            "a1",     # 2 chars with number
            "ab!",    # 3 chars with symbol
        ]

        for msg in ambiguous_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is True, f"Failed to detect ambiguity in: {msg}"
            assert result["reason"] == "too_short"

    @pytest.mark.asyncio
    async def test_detects_missing_email_format(self, session_service, sample_session):
        """Test that responses without email format when email is requested are detected."""
        # Add a bot message asking for email
        from src.models.session import Message
        bot_message = Message(
            id="12345678-1234-1234-1234-123456789013",
            session_id=sample_session.id,
            role=MessageRole.ASSISTANT,
            content="What's your email address?",
            created_at=datetime.utcnow(),
        )
        sample_session.messages = [bot_message]

        result = await session_service._check_ambiguity("john doe", sample_session)
        assert result["is_ambiguous"] is True
        assert result["reason"] == "missing_email_format"

    @pytest.mark.asyncio
    async def test_accepts_valid_name_when_asked(self, session_service, sample_session):
        """Test that valid names are accepted when name is requested."""
        # Add a bot message asking for name
        from src.models.session import Message
        bot_message = Message(
            id="12345678-1234-1234-1234-123456789013",
            session_id=sample_session.id,
            role=MessageRole.ASSISTANT,
            content="What's your name?",
            created_at=datetime.utcnow(),
        )
        sample_session.messages = [bot_message]

        valid_names = ["John", "Jane Smith", "Bob"]

        for name in valid_names:
            result = await session_service._check_ambiguity(name, sample_session)
            assert result["is_ambiguous"] is False, f"Valid name rejected: {name}"

    @pytest.mark.asyncio
    async def test_accepts_valid_email(self, session_service, sample_session):
        """Test that valid emails are accepted."""
        valid_emails = ["test@example.com", "user.name@company.co.uk"]

        for email in valid_emails:
            result = await session_service._check_ambiguity(email, sample_session)
            assert result["is_ambiguous"] is False, f"Valid email rejected: {email}"

    @pytest.mark.asyncio
    async def test_accepts_detailed_responses(self, session_service, sample_session):
        """Test that detailed responses are accepted."""
        valid_messages = [
            "I need help with my website",
            "We are a healthcare company looking for data analytics solutions",
            "Our budget is around $50,000 and we need this done in 2 months",
            "My name is John and I work at Acme Corp",
        ]

        for msg in valid_messages:
            result = await session_service._check_ambiguity(msg, sample_session)
            assert result["is_ambiguous"] is False, f"Valid message rejected: {msg}"

    @pytest.mark.asyncio
    async def test_clarification_response_generation(self, session_service, sample_session):
        """Test that clarification responses are generated correctly."""
        # Test each ambiguity type multiple times to verify all message options work
        ambiguity_types = {
            "uncertainty": ["could", "details", "understand"],
            "lack_of_knowledge": ["could", "tell", "thanks"],
            "guessing": ["could", "thanks", "specific"],
            "non_specific": ["specific", "details", "could"],
            "minimal_response": ["could", "tell", "more"],
            "hesitation": ["time", "ready", "when", "rush"],
            "too_short": ["could", "detail", "more"],
            "missing_email_format": ["email"],
        }

        for reason, expected_keywords in ambiguity_types.items():
            # Run multiple times to test random selection
            for _ in range(5):
                response = session_service._generate_clarification_response(
                    {"reason": reason},
                    "test message",
                    sample_session
                )
                # Check that response contains at least one expected keyword
                has_keyword = any(keyword.lower() in response.lower() for keyword in expected_keywords)
                assert has_keyword, \
                    f"Response for {reason} doesn't contain any expected keywords: {response}"

    @pytest.mark.asyncio
    async def test_full_ambiguity_flow(self, session_service, sample_session):
        """Test the full flow: ambiguous message -> clarification response."""
        # Mock the database commit and refresh
        session_service.db = AsyncMock()
        session_service.db.add = MagicMock()
        session_service.db.commit = AsyncMock()
        session_service.db.refresh = AsyncMock()

        # Test with an ambiguous message
        ambiguous_message = "maybe"

        # Call generate_ai_response
        result = await session_service.generate_ai_response(sample_session, ambiguous_message)

        # Verify it returned a clarification message
        assert result.role == MessageRole.ASSISTANT
        assert result.meta_data.get("type") == "clarification"
        assert result.meta_data.get("ambiguous_reason") == "uncertainty"
        assert len(result.content) > 0

        # Verify the AI service was NOT called (ambiguity detected early)
        session_service.ai_service.generate_response.assert_not_called()
