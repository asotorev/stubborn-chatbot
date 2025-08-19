"""
DebateTopic entity - represents a controversial topic and the bot's stance.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List
from uuid import UUID, uuid4


class DebateStance(Enum):
    """The stance the bot takes on a debate topic."""
    FOR = "for"
    AGAINST = "against"


class DebateTopic:
    """
    Represents a controversial topic that the bot can debate about.
    
    Contains the topic description, the bot's assigned stance,
    and key talking points for the debate.
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        bot_stance: DebateStance,
        key_arguments: List[str],
        topic_id: UUID | None = None,
        created_at: datetime | None = None,
        metadata: Dict[str, str] | None = None
    ):
        """
        Initialize a new debate topic.
        
        Args:
            title: Short title of the debate topic
            description: Detailed description of what's being debated
            bot_stance: Whether the bot argues FOR or AGAINST the topic
            key_arguments: List of main arguments the bot should use
            topic_id: Unique identifier (auto-generated if None)
            created_at: When the topic was created (auto-generated if None)
            metadata: Additional topic information
        """
        if not title or not title.strip():
            raise ValueError("Topic title cannot be empty")
        
        if not description or not description.strip():
            raise ValueError("Topic description cannot be empty")
            
        if not key_arguments:
            raise ValueError("Topic must have at least one key argument")
            
        self.topic_id = topic_id or uuid4()
        self.title = title.strip()
        self.description = description.strip()
        self.bot_stance = bot_stance
        self.key_arguments = key_arguments.copy()
        self.created_at = created_at or datetime.now(timezone.utc)
        self.metadata = metadata or {}
    
    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        bot_stance: DebateStance,
        key_arguments: List[str]
    ) -> "DebateTopic":
        """
        Convenience method to create a new debate topic.
        
        Args:
            title: Short title of the debate topic
            description: Detailed description of what's being debated
            bot_stance: Whether the bot argues FOR or AGAINST the topic
            key_arguments: List of main arguments the bot should use
            
        Returns:
            New DebateTopic instance
        """
        return cls(
            title=title,
            description=description,
            bot_stance=bot_stance,
            key_arguments=key_arguments
        )
    
    def get_stance_description(self) -> str:
        """Get a human-readable description of the bot's stance."""
        stance_word = "supports" if self.bot_stance == DebateStance.FOR else "opposes"
        return f"The bot {stance_word} the position: {self.title}"
    
    def __repr__(self) -> str:
        return f"DebateTopic(id={self.topic_id}, title='{self.title}', stance={self.bot_stance.value})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, DebateTopic):
            return False
        return self.topic_id == other.topic_id
