"""Integration tests for conversation API."""

import pytest
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase
from src.infrastructure.repositories.conversation_memory import InMemoryConversationRepository


class TestConversationFlow:
    """Test the complete conversation flow."""

    def setup_method(self):
        """Set up test dependencies."""
        self.repository = InMemoryConversationRepository()
        self.start_use_case = StartConversationUseCase(self.repository)
        self.continue_use_case = ContinueConversationUseCase(self.repository)

    def test_start_conversation_success(self):
        """Test starting a new conversation."""
        # Act
        conversation = self.start_use_case.execute("Hello, I think the earth is round")
        
        # Assert
        assert conversation.id is not None
        assert len(conversation.messages) == 2  # User message + bot response
        assert conversation.messages[0].content == "Hello, I think the earth is round"
        assert conversation.messages[0].is_from_user is True
        assert conversation.messages[1].is_from_user is False

    def test_start_conversation_empty_message(self):
        """Test starting conversation with empty message fails."""
        with pytest.raises(ValueError, match="Initial message cannot be empty"):
            self.start_use_case.execute("")

    def test_continue_conversation_success(self):
        """Test continuing an existing conversation."""
        # Arrange
        conversation = self.start_use_case.execute("Initial message")
        initial_message_count = len(conversation.messages)
        
        # Act
        updated_conversation = self.continue_use_case.execute(
            conversation.id, 
            "Follow-up message"
        )
        
        # Assert
        assert updated_conversation.id == conversation.id
        assert len(updated_conversation.messages) == initial_message_count + 2
        assert updated_conversation.messages[-2].content == "Follow-up message"
        assert updated_conversation.messages[-2].is_from_user is True
        assert updated_conversation.messages[-1].is_from_user is False

    def test_continue_conversation_not_found(self):
        """Test continuing non-existent conversation fails."""
        with pytest.raises(ValueError, match="Conversation with ID .* not found"):
            self.continue_use_case.execute("non-existent-id", "message")

    def test_continue_conversation_empty_message(self):
        """Test continuing conversation with empty message fails."""
        conversation = self.start_use_case.execute("Initial message")
        
        with pytest.raises(ValueError, match="User message cannot be empty"):
            self.continue_use_case.execute(conversation.id, "")

    def test_conversation_persistence(self):
        """Test that conversations are properly persisted."""
        # Start conversation
        conversation = self.start_use_case.execute("Test message")
        
        # Retrieve from repository directly
        retrieved = self.repository.get_by_id(conversation.id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == conversation.id
        assert len(retrieved.messages) == len(conversation.messages)
