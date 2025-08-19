"""
Repository interface for conversation persistence.

Defines the contract for storing and retrieving conversations,
independent of the actual storage mechanism.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.conversation import Conversation


class ConversationRepositoryInterface(ABC):
    """
    Abstract interface for conversation storage operations.
    
    This interface defines the contract that any conversation repository
    implementation must follow, allowing for easy swapping between
    different storage mechanisms (in-memory, Redis, database, etc.).
    """
    
    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """
        Save a conversation to storage.
        
        Args:
            conversation: The conversation to save
            
        Raises:
            RepositoryError: If the save operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.
        
        Args:
            conversation_id: The unique identifier of the conversation
            
        Returns:
            The conversation if found, None otherwise
            
        Raises:
            RepositoryError: If the retrieval operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation from storage.
        
        Args:
            conversation_id: The unique identifier of the conversation to delete
            
        Returns:
            True if the conversation was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If the delete operation fails
        """
        pass
    
    @abstractmethod
    async def exists(self, conversation_id: UUID) -> bool:
        """
        Check if a conversation exists in storage.
        
        Args:
            conversation_id: The unique identifier of the conversation
            
        Returns:
            True if the conversation exists, False otherwise
            
        Raises:
            RepositoryError: If the check operation fails
        """
        pass


class RepositoryError(Exception):
    """
    Base exception for repository operations.
    
    Raised when storage operations fail due to infrastructure issues,
    not business rule violations.
    """
    
    def __init__(self, message: str, cause: Exception | None = None):
        """
        Initialize a repository error.
        
        Args:
            message: Human-readable error description
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.cause = cause
