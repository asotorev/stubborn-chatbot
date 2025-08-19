"""
Topic service for managing debate topics.

Contains business logic for selecting and managing debate topics
that the bot can argue about. Supports both AI-generated dynamic topics
and fallback to predefined conspiracy theories.
"""

import random
from typing import List, Optional

from ..entities.debate_topic import DebateTopic, DebateStance
from ..entities.predefined_topics import get_conspiracy_topics_data
from ..interfaces.llm_service import LLMServiceInterface, LLMServiceError


class TopicService:
    """
    Service for managing and selecting debate topics.
    
    Uses AI to generate dynamic topics based on user input, with
    fallback to predefined conspiracy theories when AI fails.
    """
    
    def __init__(self, llm_service: Optional[LLMServiceInterface] = None):
        """
        Initialize the topic service.
        
        Args:
            llm_service: Optional LLM service for dynamic topic generation.
                        If None, will only use predefined topics.
        """
        self._llm_service = llm_service
        self._fallback_topics = get_conspiracy_topics_data()
        self._fallback_intros = [
            "Speaking of that, I was just thinking about how",
            "You know what's fascinating? I recently read that",
            "That reminds me of something controversial -",
            "While we're talking, did you know that",
            "Here's something that might surprise you:",
            "I've been pondering this theory lately:"
        ]
    
    async def generate_topic_for_message(self, user_message: str) -> DebateTopic:
        """
        Generate a debate topic based on user's message.
        
        First tries to use AI to generate a dynamic topic and stance.
        If AI fails or is unavailable, falls back to a random conspiracy topic.
        
        Args:
            user_message: The user's input message to analyze
            
        Returns:
            A debate topic - either AI-generated or fallback conspiracy
        """
        # Try AI-powered topic generation first
        if self._llm_service:
            try:
                return await self._llm_service.generate_debate_topic(user_message)
            except LLMServiceError:
                # AI failed, fall back to conspiracy topics
                pass
        
        # Fallback: return random conspiracy topic with intro
        return self._get_fallback_topic_with_intro()
    
    def get_random_topic(self) -> DebateTopic:
        """
        Get a random debate topic from predefined conspiracy theories.
        
        Returns:
            A randomly selected conspiracy theory topic
        """
        return random.choice(self._fallback_topics)
    
    def _get_fallback_topic_with_intro(self) -> DebateTopic:
        """
        Get a random fallback topic with a conversational intro.
        
        Adds a natural transition phrase to make the fallback feel more organic.
        
        Returns:
            A conspiracy topic with modified title including intro phrase
        """
        base_topic = self.get_random_topic()
        intro = random.choice(self._fallback_intros)
        
        # Create a new topic with intro phrase
        enhanced_title = f"{intro} {base_topic.title.lower()}"
        
        return DebateTopic(
            title=enhanced_title,
            description=base_topic.description,
            bot_stance=base_topic.bot_stance,
            key_arguments=base_topic.key_arguments.copy(),
            topic_id=base_topic.topic_id,
            created_at=base_topic.created_at,
            metadata={"is_fallback": True, "original_title": base_topic.title}
        )
