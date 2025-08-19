"""
In-memory implementation of conversation repository.

Provides a simple, fast storage solution for development and testing.
Data is lost when the application restarts.
"""

from typing import Dict, Optional
from uuid import UUID

from ...core.entities.conversation import Conversation
from ...core.interfaces.conversation_repository import ConversationRepositoryInterface, RepositoryError


class ConversationMemoryRepository(ConversationRepositoryInterface):
    """
    In-memory implementation of conversation repository.
    
    Stores conversations in a Python dictionary for fast access.
    This is ideal for development, testing, and demonstration purposes.
    Data will be lost when the application restarts.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._conversations: Dict[UUID, Conversation] = {}
    
    async def save(self, conversation: Conversation) -> None:
        """
        Save a conversation to memory.
        
        Args:
            conversation: The conversation to save
            
        Raises:
            RepositoryError: If the conversation is invalid
        """
        try:
            if not isinstance(conversation, Conversation):
                raise RepositoryError("Invalid conversation object")
            
            self._conversations[conversation.conversation_id] = conversation
            
        except Exception as e:
            raise RepositoryError(f"Failed to save conversation: {str(e)}", cause=e)
    
    async def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID from memory.
        
        Args:
            conversation_id: The unique identifier of the conversation
            
        Returns:
            The conversation if found, None otherwise
            
        Raises:
            RepositoryError: If the retrieval operation fails
        """
        try:
            return self._conversations.get(conversation_id)
            
        except Exception as e:
            raise RepositoryError(f"Failed to retrieve conversation: {str(e)}", cause=e)
    
    async def delete(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation from memory.
        
        Args:
            conversation_id: The unique identifier of the conversation to delete
            
        Returns:
            True if the conversation was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If the delete operation fails
        """
        try:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                return True
            return False
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete conversation: {str(e)}", cause=e)
    
    async def exists(self, conversation_id: UUID) -> bool:
        """
        Check if a conversation exists in memory.
        
        Args:
            conversation_id: The unique identifier of the conversation
            
        Returns:
            True if the conversation exists, False otherwise
            
        Raises:
            RepositoryError: If the check operation fails
        """
        try:
            return conversation_id in self._conversations
            
        except Exception as e:
            raise RepositoryError(f"Failed to check conversation existence: {str(e)}", cause=e)
    
    def get_conversation_count(self) -> int:
        """
        Get the total number of conversations in memory.
        
        Returns:
            Number of stored conversations
        """
        return len(self._conversations)
    
    def clear_all(self) -> None:
        """
        Clear all conversations from memory.
        
        Useful for testing and cleanup operations.
        """
        self._conversations.clear()
