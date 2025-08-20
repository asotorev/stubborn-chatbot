"""Integration tests for conversation API."""

import pytest
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase
from src.infrastructure.repositories.conversation_memory import ConversationMemoryRepository
from src.core.domain_services.topic_service import TopicService


class TestConversationFlow:
    """Test the complete conversation flow."""

    def setup_method(self):
        """Set up test dependencies."""
        self.repository = ConversationMemoryRepository()
        self.topic_service = TopicService(llm_service=None)  # Use fallback topics
        self.start_use_case = StartConversationUseCase(self.repository, self.topic_service)
        self.continue_use_case = ContinueConversationUseCase(self.repository)

    @pytest.mark.asyncio
    async def test_start_conversation_success(self):
        """Test starting a new conversation."""
        # Act
        conversation = await self.start_use_case.execute("Hello, I think the earth is round")
        
        # Assert
        assert conversation.conversation_id is not None
        assert len(conversation.get_messages()) == 2  # User message + bot response
        assert conversation.get_messages()[0].content == "Hello, I think the earth is round"
        assert conversation.get_messages()[0].role == "user"
        assert conversation.get_messages()[1].role == "bot"
        assert conversation.has_topic()  # Should have a debate topic assigned
        assert conversation.topic is not None

    @pytest.mark.asyncio
    async def test_start_conversation_empty_message(self):
        """Test starting conversation with empty message fails."""
        with pytest.raises(ValueError, match="Initial message cannot be empty"):
            await self.start_use_case.execute("")

    @pytest.mark.asyncio
    async def test_continue_conversation_success(self):
        """Test continuing an existing conversation."""
        # Arrange
        conversation = await self.start_use_case.execute("Initial message")
        initial_message_count = len(conversation.get_messages())
        
        # Act
        updated_conversation = await self.continue_use_case.execute(
            str(conversation.conversation_id), 
            "Follow-up message"
        )
        
        # Assert
        assert updated_conversation.conversation_id == conversation.conversation_id
        assert len(updated_conversation.get_messages()) == initial_message_count + 2
        assert updated_conversation.get_messages()[-2].content == "Follow-up message"
        assert updated_conversation.get_messages()[-2].role == "user"
        assert updated_conversation.get_messages()[-1].role == "bot"

    @pytest.mark.asyncio
    async def test_continue_conversation_not_found(self):
        """Test continuing non-existent conversation fails."""
        # Use a valid UUID format that doesn't exist
        fake_uuid = "12345678-1234-5678-1234-567812345678"
        with pytest.raises(ValueError, match="Conversation with ID .* not found"):
            await self.continue_use_case.execute(fake_uuid, "message")

    @pytest.mark.asyncio
    async def test_continue_conversation_empty_message(self):
        """Test continuing conversation with empty message fails."""
        conversation = await self.start_use_case.execute("Initial message")
        
        with pytest.raises(ValueError, match="User message cannot be empty"):
            await self.continue_use_case.execute(str(conversation.conversation_id), "")

    @pytest.mark.asyncio
    async def test_conversation_persistence(self):
        """Test that conversations are properly persisted."""
        # Start conversation
        conversation = await self.start_use_case.execute("Test message")
        
        # Retrieve from repository directly
        retrieved = await self.repository.get_by_id(conversation.conversation_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.conversation_id == conversation.conversation_id
        assert len(retrieved.get_messages()) == len(conversation.get_messages())
