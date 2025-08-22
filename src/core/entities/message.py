"""
Message entity - represents a single message in a conversation.
"""

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4


class Message:
    """
    Represents a single message in a debate conversation.
    
    Contains the message content, role (user or bot), and metadata.
    """
    
    def __init__(
        self,
        content: str,
        role: Literal["user", "bot"],
        message_id: UUID | None = None,
        created_at: datetime | None = None
    ):
        """
        Initialize a new message.
        
        Args:
            content: The message text content
            role: Whether this message is from 'user' or 'bot'
            message_id: Unique identifier for the message (auto-generated if None)
            created_at: When the message was created (auto-generated if None)
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")
        
        if role not in ["user", "bot"]:
            raise ValueError("Role must be either 'user' or 'bot'")
            
        self.message_id = message_id or uuid4()
        self.content = content.strip()
        self.role = role
        self.created_at = created_at or datetime.now(timezone.utc)
    
    @classmethod
    def create(
        cls,
        content: str,
        role: Literal["user", "bot"]
    ) -> "Message":
        """
        Convenience method to create a new message.
        
        Args:
            content: The message text content
            role: Whether this message is from 'user' or 'bot'
            
        Returns:
            New Message instance
        """
        return cls(content=content, role=role)
    
    def __repr__(self) -> str:
        return f"Message(id={self.message_id}, role='{self.role}', content='{self.content[:50]}...')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Message):
            return False
        return self.message_id == other.message_id
