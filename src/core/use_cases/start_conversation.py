"""Start conversation use case."""

from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface
from src.core.domain_services.topic_service import TopicService


class StartConversationUseCase:
    """Use case for starting a new conversation."""

    def __init__(
        self, 
        conversation_repository: ConversationRepositoryInterface,
        topic_service: TopicService
    ):
        self._conversation_repository = conversation_repository
        self._topic_service = topic_service

    async def execute(self, initial_message: str) -> Conversation:
        """
        Start a new conversation with an initial user message and debate topic selection.
        
        Args:
            initial_message: The first message from the user
            
        Returns:
            Conversation: The newly created conversation with assigned debate topic
            
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
            role="user"
        )
        conversation.add_message(user_message)
        
        # Generate debate topic based on user's message
        debate_topic = await self._topic_service.generate_topic_for_message(initial_message)
        
        if debate_topic is None:
            # User sent a casual greeting - respond with debate-seeking message
            bot_response_content = (
                "I hear what you're saying, but I was really looking forward to a good debate "
                "with you. What's a topic you have strong opinions about?"
            )
        else:
            # Set the debate topic for this conversation
            conversation.set_debate_topic(debate_topic)
            
            # Create bot response introducing the debate topic
            stance_word = "support" if debate_topic.bot_stance.value == "for" else "oppose"
            bot_response_content = (
                f"I actually {stance_word} the idea that {debate_topic.title.lower()}. "
                f"Here's why I believe this: {debate_topic.key_arguments[0]}. "
                f"What do you think about that?"
            )
        
        bot_response = Message.create(
            content=bot_response_content,
            role="bot"
        )
        conversation.add_message(bot_response)
        
        # Save conversation
        await self._conversation_repository.save(conversation)
        
        return conversation
