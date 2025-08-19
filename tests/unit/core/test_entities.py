"""
Tests for core domain entities.

Tests the business logic and invariants of our domain entities.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.core.entities.message import Message
from src.core.entities.debate_topic import DebateTopic, DebateStance
from src.core.entities.conversation import Conversation


class TestMessage:
    """Test cases for Message entity."""
    
    def test_create_valid_message(self):
        """Test creating a valid message."""
        message = Message.create("Hello world", "user")
        
        assert message.content == "Hello world"
        assert message.role == "user"
        assert message.message_id is not None
        assert message.created_at is not None
    
    def test_message_validation(self):
        """Test message validation rules."""
        # Empty content should raise error
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message.create("", "user")
        
        # Invalid role should raise error
        with pytest.raises(ValueError, match="Role must be either 'user' or 'bot'"):
            Message.create("Hello", "invalid")
    
    def test_message_equality(self):
        """Test message equality comparison."""
        msg_id = uuid4()
        msg1 = Message("Hello", "user", msg_id)
        msg2 = Message("Different content", "bot", msg_id)
        msg3 = Message("Hello", "user", uuid4())
        
        assert msg1 == msg2  # Same ID
        assert msg1 != msg3  # Different ID


class TestDebateTopic:
    """Test cases for DebateTopic entity."""
    
    def test_create_valid_topic(self):
        """Test creating a valid debate topic."""
        topic = DebateTopic.create(
            "Test Topic",
            "A test topic description",
            DebateStance.FOR,
            ["Argument 1", "Argument 2"]
        )
        
        assert topic.title == "Test Topic"
        assert topic.description == "A test topic description"
        assert topic.bot_stance == DebateStance.FOR
        assert len(topic.key_arguments) == 2
    
    def test_topic_validation(self):
        """Test topic validation rules."""
        # Empty title should raise error
        with pytest.raises(ValueError, match="Topic title cannot be empty"):
            DebateTopic.create("", "Description", DebateStance.FOR, ["Arg1"])
        
        # Empty arguments should raise error
        with pytest.raises(ValueError, match="Topic must have at least one key argument"):
            DebateTopic.create("Title", "Description", DebateStance.FOR, [])
    
    def test_stance_description(self):
        """Test stance description generation."""
        topic_for = DebateTopic.create("Topic", "Desc", DebateStance.FOR, ["Arg1"])
        topic_against = DebateTopic.create("Topic", "Desc", DebateStance.AGAINST, ["Arg1"])
        
        assert "supports" in topic_for.get_stance_description()
        assert "opposes" in topic_against.get_stance_description()


class TestConversation:
    """Test cases for Conversation entity."""
    
    def test_create_conversation(self):
        """Test creating a conversation."""
        topic = DebateTopic.create("Topic", "Description", DebateStance.FOR, ["Arg1"])
        conversation = Conversation.create(topic)
        
        assert conversation.topic == topic
        assert conversation.is_empty()
        assert conversation.get_message_count() == 0
    
    def test_add_messages(self):
        """Test adding messages to conversation."""
        topic = DebateTopic.create("Topic", "Description", DebateStance.FOR, ["Arg1"])
        conversation = Conversation.create(topic)
        
        # Add first message
        user_msg = Message.create("Hello", "user")
        conversation.add_message(user_msg)
        
        assert not conversation.is_empty()
        assert conversation.get_message_count() == 1
        assert conversation.get_last_message() == user_msg
    
    def test_message_alternation_rule(self):
        """Test that messages must alternate between user and bot."""
        topic = DebateTopic.create("Topic", "Description", DebateStance.FOR, ["Arg1"])
        conversation = Conversation.create(topic)
        
        # Add user message
        conversation.add_message(Message.create("User message 1", "user"))
        
        # Adding another user message should fail
        with pytest.raises(ValueError, match="Cannot add consecutive user messages"):
            conversation.add_message(Message.create("User message 2", "user"))
        
        # Adding bot message should work
        conversation.add_message(Message.create("Bot response", "bot"))
        assert conversation.get_message_count() == 2
    
    def test_recent_messages(self):
        """Test getting recent messages."""
        topic = DebateTopic.create("Topic", "Description", DebateStance.FOR, ["Arg1"])
        conversation = Conversation.create(topic)
        
        # Add several messages
        for i in range(10):
            role = "user" if i % 2 == 0 else "bot"
            conversation.add_message(Message.create(f"Message {i}", role))
        
        # Get recent messages
        recent = conversation.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[-1].content == "Message 9"  # Most recent
        assert recent[0].content == "Message 7"   # Oldest of the 3
