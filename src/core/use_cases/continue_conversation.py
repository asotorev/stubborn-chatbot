"""Continue conversation use case."""

from uuid import UUID
from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface
from src.core.interfaces.llm_service import LLMServiceInterface, LLMServiceError
from src.core.domain_services.topic_service import TopicService


class ContinueConversationUseCase:
    """Use case for continuing an existing conversation."""

    def __init__(
        self, 
        conversation_repository: ConversationRepositoryInterface,
        llm_service: LLMServiceInterface | None = None,
        topic_service: TopicService | None = None
    ):
        self._conversation_repository = conversation_repository
        self._llm_service = llm_service
        self._topic_service = topic_service

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
        
        # Generate AI-powered bot response
        bot_response_content = await self._generate_bot_response(conversation, user_message)
        
        bot_response = Message.create(
            content=bot_response_content,
            role="bot"
        )
        conversation.add_message(bot_response)
        
        # Save updated conversation
        await self._conversation_repository.save(conversation)
        
        return conversation
    
    async def _generate_bot_response(self, conversation: Conversation, user_message: str) -> str:
        """
        Generate an AI-powered bot response based on conversation context.
        
        Args:
            conversation: The conversation with topic and history
            user_message: The latest user message to respond to
            
        Returns:
            Generated bot response content
        """
        if not conversation.has_topic():
            # Try to generate a topic from this user message
            if self._topic_service:
                topic = await self._topic_service.generate_topic_for_message(user_message)
                if topic is not None:
                    # Set the topic and generate a proper debate response
                    conversation.set_debate_topic(topic)
                    stance_word = "support" if topic.bot_stance.value == "for" else "oppose"
                    return (
                        f"I actually {stance_word} the idea that {topic.title.lower()}. "
                        f"Here's why I believe this: {topic.key_arguments[0]}. "
                        f"What do you think about that?"
                    )
            
            # Still no topic - ask again but more specifically
            return "I hear what you're saying, but I was really looking forward to a good debate with you. What's a topic you have strong opinions about?"
        
        topic = conversation.topic
        
        # Try AI-powered response generation first
        if self._llm_service:
            try:
                return await self._generate_ai_response(conversation, user_message, topic)
            except LLMServiceError:
                # Fall back to template response if AI fails
                pass
        
        # Fallback to template-based response
        return self._generate_template_response(topic, user_message)
    
    async def _generate_ai_response(self, conversation: Conversation, user_message: str, topic) -> str:
        """Generate AI-powered contextual response."""
        # Check if this is the mock service (doesn't have real AI capabilities)
        if hasattr(self._llm_service, '_topics_data'):
            # This is MockOpenAIService, use enhanced template logic
            return self._generate_enhanced_mock_response(conversation, user_message, topic)
        
        # Build conversation history for context
        recent_messages = conversation.get_recent_messages(limit=6)  # Last 3 exchanges
        history = []
        for msg in recent_messages[:-1]:  # Exclude the current user message
            history.append(f"{msg.role.title()}: {msg.content}")
        
        history_context = "\n".join(history) if history else "This is the start of our conversation."
        
        # Create prompt for contextual debate response
        prompt = f"""You are debating the topic: "{topic.title}"

Your stance: {topic.get_stance_description()}

Your key arguments:
{chr(10).join(f"- {arg}" for arg in topic.key_arguments)}

Conversation history:
{history_context}

The user just said: "{user_message}"

Generate a persuasive response that:
1. Stays true to your stance on "{topic.title}"
2. Directly addresses the user's point
3. Uses one of your key arguments strategically
4. Asks a probing question to continue the debate
5. Maintains an intellectual but passionate tone

Keep your response to 2-3 sentences maximum. Be engaging and persuasive."""

        # Use the real LLM service to generate the response
        response = await self._llm_service._client.chat.completions.create(
            model=self._llm_service._model,
            messages=[
                {"role": "system", "content": "You are a skilled debater who stays on topic and argues persuasively."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_enhanced_mock_response(self, conversation: Conversation, user_message: str, topic) -> str:
        """Generate enhanced mock response with more context awareness."""
        import random
        
        # Analyze user message for key words to make response more contextual
        user_lower = user_message.lower()
        
        # Select argument based on user's content if possible
        relevant_arguments = []
        for arg in topic.key_arguments:
            # Simple keyword matching to find relevant arguments
            arg_keywords = arg.lower().split()
            if any(keyword in user_lower for keyword in arg_keywords[:3]):
                relevant_arguments.append(arg)
        
        # Use relevant argument if found, otherwise random
        argument = random.choice(relevant_arguments) if relevant_arguments else random.choice(topic.key_arguments)
        
        # Contextual response starters based on conversation length
        message_count = len(conversation.get_recent_messages())
        
        if message_count <= 2:  # Early in conversation
            starters = [
                "That's exactly what I'd expect you to say, but",
                "I understand that perspective, however",
                "Many people think that way, but here's the thing:",
            ]
        else:  # Deeper in conversation
            starters = [
                "You're still missing the key point:",
                "Let me put this differently:",
                "I can see you're not convinced yet, but",
                "You keep ignoring this crucial fact:",
            ]
        
        starter = random.choice(starters)
        
        # Engaging endings
        endings = [
            "How do you explain that?",
            "What's your response to this evidence?",
            "Doesn't this change everything?",
            "Can you really deny this logic?",
            "How do you reconcile this with your position?",
        ]
        
        ending = random.choice(endings)
        
        return f"{starter} {argument} {ending}"
    
    def _generate_template_response(self, topic, user_message: str) -> str:
        """Generate template-based response as fallback."""
        import random
        
        # Select a random key argument to use
        argument = random.choice(topic.key_arguments)
        
        # Variety of response templates
        templates = [
            f"Interesting point! But I still maintain that {topic.title.lower()}. Consider this: {argument}. How do you respond to that evidence?",
            f"I see your perspective, but I have to disagree. {argument}. What's your take on this?",
            f"That's a common viewpoint, but here's why I believe {topic.title.lower()}: {argument}. Doesn't this change your mind?",
            f"I understand where you're coming from, but {argument}. How do you reconcile this with your position?",
        ]
        
        return random.choice(templates)
