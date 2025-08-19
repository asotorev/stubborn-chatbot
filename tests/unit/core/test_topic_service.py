"""
Tests for the enhanced TopicService with AI integration.

Tests both AI-powered topic generation and fallback to conspiracy theories.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from src.core.domain_services.topic_service import TopicService
from src.core.entities.debate_topic import DebateTopic, DebateStance
from src.core.interfaces.llm_service import LLMServiceInterface, LLMServiceError


class TestTopicService:
    """Test cases for enhanced TopicService."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service for testing."""
        mock = Mock(spec=LLMServiceInterface)
        mock.generate_debate_topic = AsyncMock()
        mock.health_check = AsyncMock(return_value=True)
        return mock
    
    @pytest.fixture
    def topic_service_with_ai(self, mock_llm_service):
        """Create TopicService with AI enabled."""
        return TopicService(llm_service=mock_llm_service)
    
    @pytest.fixture
    def topic_service_without_ai(self):
        """Create TopicService without AI (fallback only)."""
        return TopicService(llm_service=None)
    
    @pytest.fixture
    def sample_ai_topic(self):
        """Sample topic that AI might generate."""
        return DebateTopic.create(
            title="The Earth is actually flat, not round",
            description="The Earth is not a sphere but a flat plane, and space agencies have been lying to us",
            bot_stance=DebateStance.FOR,
            key_arguments=[
                "NASA photos are clearly doctored and fake",
                "Water is always flat - it would spill off a spinning ball Earth",
                "No one has ever felt the Earth spinning at 1000 mph",
                "The horizon always appears flat to the naked eye",
                "If Earth were spinning, planes couldn't land on runways moving at 1000 mph"
            ]
        )
    
    @pytest.mark.asyncio
    async def test_ai_topic_generation_success(self, topic_service_with_ai, mock_llm_service, sample_ai_topic):
        """Test successful AI topic generation."""
        # Setup mock to return our sample topic
        mock_llm_service.generate_debate_topic.return_value = sample_ai_topic
        
        # Generate topic
        result = await topic_service_with_ai.generate_topic_for_message("I love social media")
        
        # Verify AI was called
        mock_llm_service.generate_debate_topic.assert_called_once_with("I love social media")
        
        # Verify result
        assert result == sample_ai_topic
        assert result.title == "The Earth is actually flat, not round"
        assert len(result.key_arguments) == 5
    
    @pytest.mark.asyncio
    async def test_ai_failure_fallback_to_conspiracy(self, topic_service_with_ai, mock_llm_service):
        """Test fallback to conspiracy topics when AI fails."""
        # Setup mock to raise error
        mock_llm_service.generate_debate_topic.side_effect = LLMServiceError("API failed")
        
        # Generate topic
        result = await topic_service_with_ai.generate_topic_for_message("I love space")
        
        # Verify AI was attempted
        mock_llm_service.generate_debate_topic.assert_called_once_with("I love space")
        
        # Verify fallback was used
        assert result is not None
        assert isinstance(result, DebateTopic)
        assert result.metadata.get("is_fallback") is True
        assert result.metadata.get("original_title") is not None
        
        # Check that intro phrase was added
        intro_phrases = [
            "Speaking of that, I was just thinking about how",
            "You know what's fascinating? I recently read that",
            "That reminds me of something controversial -",
            "While we're talking, did you know that",
            "Here's something that might surprise you:",
            "I've been pondering this theory lately:"
        ]
        title_starts_with_intro = any(result.title.startswith(intro) for intro in intro_phrases)
        assert title_starts_with_intro
    
    @pytest.mark.asyncio
    async def test_no_ai_service_uses_fallback(self, topic_service_without_ai):
        """Test that service without AI always uses fallback."""
        result = await topic_service_without_ai.generate_topic_for_message("Any message")
        
        # Should get fallback topic
        assert result is not None
        assert isinstance(result, DebateTopic)
        assert result.metadata.get("is_fallback") is True
    
    def test_get_random_topic(self, topic_service_without_ai):
        """Test getting random conspiracy topic."""
        topic = topic_service_without_ai.get_random_topic()
        
        assert isinstance(topic, DebateTopic)
        assert topic.bot_stance == DebateStance.FOR
        assert len(topic.key_arguments) > 0
        
        # Should be one of our conspiracy topics
        expected_titles = [
            "The Earth is actually flat, not round",
            "The 1969 moon landing was staged in Hollywood",
            "World leaders are secretly reptilian aliens in disguise",
            "Vaccines are more dangerous than helpful",
            "Climate change is a hoax created by governments"
        ]
        assert topic.title in expected_titles
    
    def test_fallback_intro_phrases_variety(self, topic_service_without_ai):
        """Test that fallback topics use different intro phrases."""
        intros_used = set()
        
        # Generate multiple fallback topics
        for _ in range(20):
            topic = topic_service_without_ai._get_fallback_topic_with_intro()
            # Extract the intro phrase (everything before the original title)
            original_title = topic.metadata["original_title"].lower()
            intro = topic.title.replace(original_title, "").strip()
            intros_used.add(intro)
        
        # Should have used multiple different intro phrases
        assert len(intros_used) > 1
    
    def test_fallback_topic_metadata(self, topic_service_without_ai):
        """Test that fallback topics have correct metadata."""
        topic = topic_service_without_ai._get_fallback_topic_with_intro()
        
        assert topic.metadata["is_fallback"] is True
        assert "original_title" in topic.metadata
        assert isinstance(topic.metadata["original_title"], str)
        assert len(topic.metadata["original_title"]) > 0
