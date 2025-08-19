"""Start conversation use case."""

from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface


class StartConversationUseCase:
    """Use case for starting a new conversation."""

    def __init__(self, conversation_repository: ConversationRepositoryInterface):
        self._conversation_repository = conversation_repository

    def execute(self, initial_message: str) -> Conversation:
        """
        Start a new conversation with an initial user message.
        
        Args:
            initial_message: The first message from the user
            
        Returns:
            Conversation: The newly created conversation
            
        Raises:
            ValueError: If initial_message is empty or invalid
        """
        if not initial_message or not initial_message.strip():
            raise ValueError("Initial message cannot be empty")

        # Create new conversation
        conversation = Conversation.create()
        
        # Add the user's initial message
        user_message = Message.create(
            content=initial_message.strip(),
            is_from_user=True
        )
        conversation.add_message(user_message)
        
        # For now, add a simple bot response
        # TODO: This will be replaced with AI-generated responses in later commits
        bot_response = Message.create(
            content="Hello! I'm ready to debate. What's your position on this topic?",
            is_from_user=False
        )
        conversation.add_message(bot_response)
        
        # Save conversation
        self._conversation_repository.save(conversation)
        
        return conversation
