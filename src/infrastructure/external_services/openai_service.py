"""
OpenAI service implementation for dynamic topic generation.

Provides AI-powered analysis of user messages to generate
controversial debate topics and stances.
"""

import json
import logging
from typing import Dict, Any

import openai

from ...core.entities.debate_topic import DebateTopic, DebateStance
from ...core.entities.predefined_topics import get_conspiracy_topics_data
from ...core.interfaces.llm_service import LLMServiceInterface, LLMServiceError

logger = logging.getLogger(__name__)


class OpenAIService(LLMServiceInterface):
    """
    OpenAI-powered implementation of LLM service.
    
    Uses OpenAI's GPT models to analyze user messages and generate
    controversial debate topics with supporting arguments.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI service.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._model = model
        
        # System prompt for generating controversial stances
        self._system_prompt = """You are a debate topic generator. Your job is to:

1. Analyze the user's message to identify the main topic they're discussing
2. Generate a controversial or contrarian stance on that topic
3. Provide 3-5 compelling arguments supporting that stance

Rules:
- The stance should be debatable but not offensive or harmful
- Arguments should be persuasive and based on real talking points (even if disputed)
- Keep the tone intellectual, not inflammatory
- Focus on topics where reasonable people can disagree

Return ONLY a JSON object with this exact structure:
{
    "title": "Your controversial stance as a clear statement",
    "description": "Brief explanation of what this stance means",
    "key_arguments": ["Argument 1", "Argument 2", "Argument 3", "Argument 4", "Argument 5"]
}"""
    
    async def generate_debate_topic(self, user_message: str) -> DebateTopic:
        """
        Generate a debate topic and controversial stance based on user input.
        
        Args:
            user_message: The user's input message to analyze
            
        Returns:
            A DebateTopic with a controversial stance for the bot to defend
            
        Raises:
            LLMServiceError: If topic generation fails
        """
        try:
            logger.info(f"Generating debate topic for message: {user_message[:100]}...")
            
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": f"Generate a controversial stance based on this message: {user_message}"}
                ],
                max_tokens=500,
                temperature=0.8  # Add some creativity
            )
            
            content = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI response: {content}")
            
            # Parse the JSON response
            topic_data = json.loads(content)
            
            # Validate required fields
            required_fields = ["title", "description", "key_arguments"]
            for field in required_fields:
                if field not in topic_data:
                    raise LLMServiceError(f"Missing required field: {field}")
            
            # Create DebateTopic entity
            return DebateTopic.create(
                title=topic_data["title"],
                description=topic_data["description"],
                bot_stance=DebateStance.FOR,  # Bot always argues FOR the controversial stance
                key_arguments=topic_data["key_arguments"]
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            raise LLMServiceError("Invalid response format from AI service", cause=e)
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMServiceError(f"Failed to generate topic: {str(e)}", cause=e)
    
    async def health_check(self) -> bool:
        """
        Check if the OpenAI service is available and responding.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        try:
            # Simple test request
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return response.choices[0].message.content is not None
            
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False


class MockOpenAIService(LLMServiceInterface):
    """
    Mock implementation for testing and development without API key.
    
    Uses shared conspiracy topic data instead of calling OpenAI API.
    """
    
    def __init__(self):
        """Initialize the mock service with shared conspiracy topics."""
        # Load shared topic data
        self._topics_data = get_conspiracy_topics_data()
        self._response_index = 0
    
    async def generate_debate_topic(self, user_message: str) -> DebateTopic:
        """Generate a mock debate topic using shared conspiracy theories."""
        # Cycle through shared conspiracy topics
        topic_data = self._topics_data[self._response_index % len(self._topics_data)]
        self._response_index += 1
        
        # Create a fresh DebateTopic entity from the existing entity
        return DebateTopic.create(
            title=topic_data.title,
            description=topic_data.description,
            bot_stance=topic_data.bot_stance,
            key_arguments=topic_data.key_arguments.copy()
        )
    
    async def health_check(self) -> bool:
        """Mock health check always returns True."""
        return True
