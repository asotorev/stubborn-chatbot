"""Continue conversation use case."""

from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface


class ContinueConversationUseCase:
    """Use case for continuing an existing conversation."""

    def __init__(self, conversation_repository: ConversationRepositoryInterface):
        self._conversation_repository = conversation_repository

    def execute(self, conversation_id: str, user_message: str) -> Conversation:
        """
        Continue an existing conversation with a new user message.
        
        Args:
            conversation_id: ID of the existing conversation
            user_message: New message from the user
            
        Returns:
            Conversation: The updated conversation
            
        Raises:
            ValueError: If conversation not found or user_message is invalid
        """
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty")

        # Retrieve existing conversation
        conversation = self._conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise ValueError(f"Conversation with ID {conversation_id} not found")

        # Add the user's new message
        new_user_message = Message.create(
            content=user_message.strip(),
            is_from_user=True
        )
        conversation.add_message(new_user_message)
        
        # For now, add a simple bot response
        # TODO: This will be replaced with AI-generated responses in later commits
        bot_response = Message.create(
            content="Interesting point! Let me counter with this perspective...",
            is_from_user=False
        )
        conversation.add_message(bot_response)
        
        # Save updated conversation
        self._conversation_repository.save(conversation)
        
        return conversation
