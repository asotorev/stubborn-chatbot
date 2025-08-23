"""
Integration tests for real OpenAI API functionality.

These tests only run when a real OpenAI API key is configured.
They test the actual AI integration with live API calls.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.config import get_settings
from src.adapters.dependency_injection.container import get_llm_service
from src.infrastructure.external_services.openai_service import OpenAIService
import asyncio


# Skip all tests in this module if no real OpenAI API key is configured
pytestmark = pytest.mark.skipif(
    not get_settings().has_openai_key,
    reason="Real OpenAI API key not configured - skipping real API tests"
)


class TestRealOpenAIIntegration:
    """Test real OpenAI API integration when API key is available."""
    
    def setup_method(self):
        """Set up test client and verify we have real OpenAI service."""
        self.client = TestClient(app)
        self.llm_service = get_llm_service()
        assert isinstance(self.llm_service, OpenAIService), "Expected real OpenAI service"
    
    def test_real_topic_generation(self):
        """Test that real OpenAI generates relevant, contextual topics."""
        test_cases = [
            {
                "user_input": "I think renewable energy is the future",
                "expected_keywords": ["renewable", "energy", "solar", "wind", "fossil", "nuclear", "grid"]
            },
            {
                "user_input": "Social media is great for connecting people", 
                "expected_keywords": ["social", "media", "connection", "isolation", "mental", "privacy"]
            },
            {
                "user_input": "Artificial intelligence will help humanity",
                "expected_keywords": ["AI", "artificial", "intelligence", "automation", "jobs", "safety"]
            }
        ]
        
        async def run_test():
            for case in test_cases:
                topic = await self.llm_service.generate_debate_topic(case["user_input"])
                
                # Verify topic structure
                assert topic.title, "Topic should have a title"
                assert topic.description, "Topic should have a description"
                assert len(topic.key_arguments) >= 3, "Topic should have at least 3 arguments"
                assert topic.bot_stance.value == "for", "Bot should always argue FOR the controversial stance"
                
                # Verify topic relevance (at least some keywords should match)
                topic_text = f"{topic.title} {topic.description}".lower()
                matching_keywords = [kw for kw in case["expected_keywords"] if kw in topic_text]
                assert len(matching_keywords) > 0, f"Topic should be relevant to input. Topic: {topic.title}"
                
                print(f"✅ Input: {case['user_input']}")
                print(f"   Generated: {topic.title}")
                print(f"   Relevant keywords found: {matching_keywords}")
        
        asyncio.run(run_test())
    
    def test_real_conversation_flow_with_context(self):
        """Test complete conversation flow with real AI maintaining context."""
        # Start conversation about a specific topic
        start_response = self.client.post(
            "/conversation",
            json={
                "conversation_id": None,
                "message": "I believe electric cars are environmentally friendly"
            }
        )
        
        assert start_response.status_code == 200
        start_data = start_response.json()
        conversation_id = start_data["conversation_id"]
        
        # Verify AI generated a relevant contrarian stance
        bot_initial_response = start_data["messages"][1]["message"]
        assert len(bot_initial_response) > 50, "Bot response should be substantial"
        
        # Continue conversation with specific counter-argument
        continue_response = self.client.post(
            "/conversation",
            json={
                "conversation_id": conversation_id,
                "message": "But electric cars produce zero direct emissions"
            }
        )
        
        assert continue_response.status_code == 200
        continue_data = continue_response.json()
        
        # Verify AI maintained context and provided relevant counter-response
        bot_follow_up = continue_data["messages"][-1]["message"]
        assert len(bot_follow_up) > 30, "Follow-up response should be substantial"
        
        # The AI should reference the conversation context
        # (This is a basic check - real AI should maintain topic consistency)
        assert bot_follow_up != bot_initial_response, "Responses should be different"
        
        print(f"✅ Initial bot stance: {bot_initial_response[:100]}...")
        print(f"✅ Contextual follow-up: {bot_follow_up[:100]}...")
    
    def test_real_ai_response_quality(self):
        """Test that real AI responses meet quality standards."""
        # Test with a challenging topic that requires nuanced response
        start_response = self.client.post(
            "/conversation",
            json={
                "conversation_id": None,
                "message": "Universal basic income would solve poverty"
            }
        )
        
        assert start_response.status_code == 200
        data = start_response.json()
        bot_response = data["messages"][1]["message"]
        
        # Quality checks for AI-generated content
        assert len(bot_response) > 80, "Response should be detailed"
        assert "?" in bot_response, "Should ask engaging questions"
        assert not bot_response.isupper(), "Should not be all caps"
        assert not bot_response.islower(), "Should have proper capitalization"
        
        # Should contain debate-like language or stance indicators  
        debate_indicators = [
            "but", "however", "consider", "argue", "evidence", "perspective", 
            "claim", "assert", "maintain", "contend", "position", "support", 
            "oppose", "believe", "think", "actually", "may not", "will not"
        ]
        response_lower = bot_response.lower()
        found_indicators = [indicator for indicator in debate_indicators if indicator in response_lower]
        assert len(found_indicators) > 0, f"Response should contain debate language. Response: {bot_response}"
        
        print(f"✅ Quality AI response: {bot_response[:150]}...")
        print(f"✅ Debate indicators found: {found_indicators}")
    
    def test_real_ai_topic_variety(self):
        """Test that AI generates varied topics for different inputs."""
        test_inputs = [
            "I love pineapple on pizza",
            "Working from home is more productive", 
            "Cryptocurrency is the future of money",
            "Video games are a waste of time"
        ]
        
        async def run_variety_test():
            generated_topics = []
            
            for user_input in test_inputs:
                topic = await self.llm_service.generate_debate_topic(user_input)
                generated_topics.append(topic.title)
                print(f"✅ '{user_input}' → '{topic.title}'")
            
            # All topics should be different
            unique_topics = set(generated_topics)
            assert len(unique_topics) == len(generated_topics), "All generated topics should be unique"
            
            # Topics should be reasonably different in content
            for i, topic1 in enumerate(generated_topics):
                for j, topic2 in enumerate(generated_topics[i+1:], i+1):
                    # Simple similarity check - topics shouldn't share too many words
                    words1 = set(topic1.lower().split())
                    words2 = set(topic2.lower().split())
                    common_words = words1.intersection(words2)
                    similarity_ratio = len(common_words) / max(len(words1), len(words2))
                    assert similarity_ratio < 0.7, f"Topics too similar: '{topic1}' vs '{topic2}'"
        
        asyncio.run(run_variety_test())
    
    def test_real_ai_health_check(self):
        """Test that real OpenAI service health check works."""
        async def run_health_test():
            is_healthy = await self.llm_service.health_check()
            assert is_healthy, "OpenAI service should be healthy with valid API key"
        
        asyncio.run(run_health_test())


class TestRealOpenAIPerformance:
    """Performance tests for real OpenAI integration."""
    
    def setup_method(self):
        """Set up for performance tests."""
        self.client = TestClient(app)
    
    def test_conversation_response_time(self):
        """Test that conversation responses come back in reasonable time."""
        import time
        
        start_time = time.time()
        response = self.client.post(
            "/conversation",
            json={
                "conversation_id": None,
                "message": "I think remote work is better than office work"
            }
        )
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should respond within 30 seconds (OpenAI can be slow sometimes)
        assert response_time < 30, f"Response took {response_time:.2f}s, should be under 30s"
        
        print(f"✅ Response time: {response_time:.2f} seconds")
        
        # Continue conversation should be faster (no topic generation)
        conversation_id = response.json()["conversation_id"]
        
        start_time = time.time()
        continue_response = self.client.post(
            "/conversation",
            json={
                "conversation_id": conversation_id,
                "message": "Remote work increases productivity"
            }
        )
        end_time = time.time()
        
        assert continue_response.status_code == 200
        continue_time = end_time - start_time
        assert continue_time < 25, f"Continue response took {continue_time:.2f}s, should be under 25s"
        
        print(f"✅ Continue response time: {continue_time:.2f} seconds")
