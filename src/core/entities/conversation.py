"""
Conversation entity - represents a debate conversation between user and bot.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from .message import Message
from .debate_topic import DebateTopic


class Conversation:
    """
    Represents a complete debate conversation.
    
    Contains the conversation history, debate topic, and business rules
    for managing the conversation state.
    """
    
    def __init__(
        self,
        topic: Optional[DebateTopic] = None,
        conversation_id: UUID | None = None,
        created_at: datetime | None = None,
        messages: List[Message] | None = None
    ):
        """
        Initialize a new conversation.
        
        Args:
            topic: The debate topic for this conversation (can be set later)
            conversation_id: Unique identifier (auto-generated if None)
            created_at: When the conversation started (auto-generated if None)
            messages: Initial messages (empty list if None)
        """
        self.conversation_id = conversation_id or uuid4()
        self.topic = topic
        self.created_at = created_at or datetime.now(timezone.utc)
        self._messages: List[Message] = messages or []
    
    @classmethod
    def create(cls, topic: Optional[DebateTopic] = None) -> "Conversation":
        """
        Convenience method to create a new conversation.
        
        Args:
            topic: The debate topic for this conversation (optional)
            
        Returns:
            New Conversation instance
        """
        return cls(topic=topic)
    
    def add_message(self, message: Message) -> None:
        """
        Add a new message to the conversation.
        
        Args:
            message: The message to add
            
        Raises:
            ValueError: If message is invalid or violates business rules
        """
        if not isinstance(message, Message):
            raise ValueError("Message must be a Message instance")
        
        # Business rule: Messages must alternate between user and bot
        # (except for the first message which can be from either)
        if self._messages:
            last_message = self._messages[-1]
            if last_message.role == message.role:
                raise ValueError(f"Cannot add consecutive {message.role} messages")
        
        self._messages.append(message)
    
    def get_messages(self) -> List[Message]:
        """
        Get all messages in the conversation.
        
        Returns:
            List of messages in chronological order
        """
        return self._messages.copy()
    
    def get_recent_messages(self, limit: int = 5) -> List[Message]:
        """
        Get the most recent messages from the conversation.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of most recent messages (up to limit)
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")
            
        return self._messages[-limit:]
    
    def get_message_count(self) -> int:
        """Get the total number of messages in the conversation."""
        return len(self._messages)
    
    def get_last_message(self) -> Optional[Message]:
        """
        Get the most recent message in the conversation.
        
        Returns:
            The last message, or None if conversation is empty
        """
        return self._messages[-1] if self._messages else None
    
    def is_empty(self) -> bool:
        """Check if the conversation has no messages."""
        return len(self._messages) == 0
    
    def set_debate_topic(self, topic: DebateTopic) -> None:
        """
        Set or update the debate topic for this conversation.
        
        Args:
            topic: The debate topic to assign
            
        Raises:
            ValueError: If topic is invalid
        """
        if not isinstance(topic, DebateTopic):
            raise ValueError("Topic must be a DebateTopic instance")
        self.topic = topic
    
    def has_topic(self) -> bool:
        """Check if the conversation has a debate topic assigned."""
        return self.topic is not None
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation state.
        
        Returns:
            String describing the conversation
        """
        message_count = len(self._messages)
        if self.topic:
            return (
                f"Conversation about '{self.topic.title}' "
                f"({self.topic.bot_stance.value}) "
                f"with {message_count} messages"
            )
        else:
            return f"Conversation with {message_count} messages (no topic assigned)"
    
    def __repr__(self) -> str:
        topic_title = self.topic.title if self.topic else "No topic"
        return (
            f"Conversation(id={self.conversation_id}, "
            f"topic='{topic_title}', "
            f"messages={len(self._messages)})"
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Conversation):
            return False
        return self.conversation_id == other.conversation_id
