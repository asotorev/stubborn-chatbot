"""
Tests for repository implementations.

Tests the data access layer implementations.
"""

import pytest
from uuid import uuid4

from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.entities.debate_topic import DebateTopic, DebateStance
from src.infrastructure.repositories.conversation_memory import ConversationMemoryRepository


class TestConversationMemoryRepository:
    """Test cases for in-memory conversation repository."""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test."""
        return ConversationMemoryRepository()
    
    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation for testing."""
        topic = DebateTopic.create(
            "Test Topic",
            "A test topic description",
            DebateStance.FOR,
            ["Argument 1", "Argument 2"]
        )
        conversation = Conversation.create(topic)
        conversation.add_message(Message.create("Hello", "user"))
        return conversation
    
    @pytest.mark.asyncio
    async def test_save_and_retrieve_conversation(self, repository, sample_conversation):
        """Test saving and retrieving a conversation."""
        # Save conversation
        await repository.save(sample_conversation)
        
        # Retrieve conversation
        retrieved = await repository.get_by_id(sample_conversation.conversation_id)
        
        assert retrieved is not None
        assert retrieved.conversation_id == sample_conversation.conversation_id
        assert retrieved.topic.title == sample_conversation.topic.title
        assert retrieved.get_message_count() == 1
    
    @pytest.mark.asyncio
    async def test_conversation_not_found(self, repository):
        """Test retrieving non-existent conversation."""
        non_existent_id = uuid4()
        result = await repository.get_by_id(non_existent_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_conversation_exists(self, repository, sample_conversation):
        """Test checking if conversation exists."""
        # Should not exist initially
        exists_before = await repository.exists(sample_conversation.conversation_id)
        assert not exists_before
        
        # Save conversation
        await repository.save(sample_conversation)
        
        # Should exist now
        exists_after = await repository.exists(sample_conversation.conversation_id)
        assert exists_after
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, repository, sample_conversation):
        """Test deleting a conversation."""
        # Save conversation
        await repository.save(sample_conversation)
        
        # Delete conversation
        deleted = await repository.delete(sample_conversation.conversation_id)
        assert deleted is True
        
        # Should not exist anymore
        exists = await repository.exists(sample_conversation.conversation_id)
        assert not exists
        
        # Deleting again should return False
        deleted_again = await repository.delete(sample_conversation.conversation_id)
        assert deleted_again is False
    
    def test_conversation_count(self, repository):
        """Test getting conversation count."""
        assert repository.get_conversation_count() == 0
        
        # This is a sync test, so we'll test the internal state directly
        topic = DebateTopic.create("Test", "Test", DebateStance.FOR, ["Arg"])
        conv = Conversation.create(topic)
        repository._conversations[conv.conversation_id] = conv
        
        assert repository.get_conversation_count() == 1
    
    def test_clear_all(self, repository):
        """Test clearing all conversations."""
        # Add some conversations directly to internal storage for testing
        topic = DebateTopic.create("Test", "Test", DebateStance.FOR, ["Arg"])
        conv1 = Conversation.create(topic)
        conv2 = Conversation.create(topic)
        
        repository._conversations[conv1.conversation_id] = conv1
        repository._conversations[conv2.conversation_id] = conv2
        
        assert repository.get_conversation_count() == 2
        
        repository.clear_all()
        assert repository.get_conversation_count() == 0
