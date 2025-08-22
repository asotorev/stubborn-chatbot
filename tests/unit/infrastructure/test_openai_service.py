"""
Tests for OpenAI service implementation.

Tests both the real OpenAI service and mock implementation.
"""

import pytest
from unittest.mock import Mock, patch

from src.infrastructure.external_services.openai_service import MockOpenAIService
from src.core.entities.debate_topic import DebateTopic, DebateStance


class TestMockOpenAIService:
    """Test cases for MockOpenAIService."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a MockOpenAIService for testing."""
        return MockOpenAIService()
    
    @pytest.mark.asyncio
    async def test_generate_debate_topic(self, mock_service):
        """Test mock topic generation."""
        topic = await mock_service.generate_debate_topic("I love technology")
        
        assert isinstance(topic, DebateTopic)
        assert topic.bot_stance == DebateStance.FOR
        assert len(topic.key_arguments) >= 3
        assert len(topic.title) > 0
        assert len(topic.description) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_topics_cycle_through_responses(self, mock_service):
        """Test that mock service cycles through different responses."""
        topics = []
        for i in range(5):
            topic = await mock_service.generate_debate_topic(f"Message {i}")
            topics.append(topic.title)
        
        # Should have at least 2 different topics (cycling through responses)
        unique_topics = set(topics)
        assert len(unique_topics) >= 2
    
    @pytest.mark.asyncio
    async def test_health_check_always_true(self, mock_service):
        """Test that mock health check always returns True."""
        result = await mock_service.health_check()
        assert result is True
