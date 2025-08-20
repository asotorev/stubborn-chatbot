"""Continue conversation use case."""

from uuid import UUID
from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface


class ContinueConversationUseCase:
    """Use case for continuing an existing conversation."""

    def __init__(self, conversation_repository: ConversationRepositoryInterface):
        self._conversation_repository = conversation_repository

    async def execute(self, conversation_id: str, user_message: str) -> Conversation:
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
        try:
            conversation_uuid = UUID(conversation_id)
        except ValueError:
            raise ValueError(f"Invalid conversation ID format: {conversation_id}")
            
        conversation = await self._conversation_repository.get_by_id(conversation_uuid)
        if conversation is None:
            raise ValueError(f"Conversation with ID {conversation_id} not found")

        # Add the user's new message
        new_user_message = Message.create(
            content=user_message.strip(),
            role="user"
        )
        conversation.add_message(new_user_message)
        
        # Generate bot response based on debate topic
        if conversation.has_topic():
            # Use debate topic to create contextual response
            topic = conversation.topic
            import random
            
            # Select a random key argument to use
            argument = random.choice(topic.key_arguments)
            
            bot_response_content = (
                f"Interesting point! But I still maintain that {topic.title.lower()}. "
                f"Consider this: {argument}. "
                f"How do you respond to that evidence?"
            )
        else:
            # Fallback for conversations without topics
            bot_response_content = "Interesting point! Let me counter with this perspective..."
        
        bot_response = Message.create(
            content=bot_response_content,
            role="bot"
        )
        conversation.add_message(bot_response)
        
        # Save updated conversation
        await self._conversation_repository.save(conversation)
        
        return conversation
