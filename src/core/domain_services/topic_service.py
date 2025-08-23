"""
Topic service for managing debate topics.

Contains business logic for selecting and managing debate topics
that the bot can argue about. Supports both AI-generated dynamic topics
and fallback to predefined conspiracy theories.
"""

import random
import re
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
    
    def _is_casual_greeting(self, message: str) -> bool:
        """
        Detect if the user message is a casual greeting that shouldn't generate a topic.
        
        A message is considered a greeting only if:
        1. It's primarily a greeting (greeting words are the main content)
        2. Not when greeting words are just politeness before substantial content
        
        Args:
            message: The user's message
            
        Returns:
            True if the message is a casual greeting, False otherwise
        """
        message_lower = message.lower().strip()
        words = message_lower.split()
        
        # Pure greeting patterns that indicate the message is only/primarily a greeting
        pure_greeting_patterns = [
            # Single word greetings
            "hi", "hello", "hey", "sup", "yo", "howdy",
            # Common greeting phrases
            "how are you", "what's up", "whats up", "how do you do", 
            "good morning", "good afternoon", "good evening",
            "nice to meet you", "pleased to meet you", 
            "how's it going", "hows it going", "what up"
        ]
        
        # Check if the entire message (or most of it) is just a greeting
        for pattern in pure_greeting_patterns:
            if pattern == message_lower:
                # Exact match - definitely a greeting
                return True
            elif pattern in message_lower:
                # Pattern found - check if it's the main content
                pattern_words = len(pattern.split())
                total_words = len(words)
                
                # If greeting takes up most of the message (>50%), it's primarily a greeting
                if pattern_words / total_words > 0.5:
                    return True
                
                # Special cases for short messages with greetings at the start
                # Only if the message is short AND doesn't contain substantial content words
                if message_lower.startswith(pattern) and total_words <= 4:
                    return True
                elif message_lower.startswith(pattern) and total_words <= 6:
                    # Check if there are substantial content words after the greeting
                    remaining_text = message_lower[len(pattern):].strip()
                    substantial_words = ["think", "believe", "love", "hate", "support", "oppose", "about", "regarding"]
                    if not any(word in remaining_text for word in substantial_words):
                        return True
        
        # Additional check: if message contains multiple distinct greeting elements, it's likely a greeting
        # Use word boundaries to avoid false matches (like "hi" inside "think")
        greeting_elements = 0
        for pattern in pure_greeting_patterns:
            # Create regex pattern with word boundaries for single words
            if " " not in pattern:  # Single word
                if re.search(r'\b' + re.escape(pattern) + r'\b', message_lower):
                    greeting_elements += 1
            else:  # Multi-word phrase
                if pattern in message_lower:
                    greeting_elements += 1
        
        if greeting_elements >= 2 and len(words) <= 8:
            return True
        
        return False
    
    async def generate_topic_for_message(self, user_message: str) -> Optional[DebateTopic]:
        """
        Generate a debate topic based on user's message.
        
        First tries to use AI to generate a dynamic topic and stance.
        If AI fails or is unavailable, falls back to a random conspiracy topic.
        
        Args:
            user_message: The user's input message to analyze
            
        Returns:
            A debate topic - either AI-generated or fallback conspiracy, 
            or None if the message is a casual greeting
        """
        # Check if message is too casual/greeting-like for topic generation
        if self._is_casual_greeting(user_message):
            return None  # Signal that no topic should be generated yet
        
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
