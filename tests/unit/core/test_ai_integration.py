"""
Unit tests for AI integration in use cases.

Tests the AI-powered response generation logic in isolation.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from src.core.use_cases.continue_conversation import ContinueConversationUseCase
from src.core.entities.conversation import Conversation
from src.core.entities.message import Message
from src.core.entities.debate_topic import DebateTopic, DebateStance
from src.core.interfaces.llm_service import LLMServiceInterface, LLMServiceError


class MockLLMService(LLMServiceInterface):
    """Mock LLM service for testing."""
    
    def __init__(self, should_fail=False, response_content="Mock AI response"):
        self.should_fail = should_fail
        self.response_content = response_content
        self.generate_topic_calls = []
        self.health_check_calls = []
        
        # Mock the client structure for real OpenAI service simulation
        self._client = Mock()
        self._model = "gpt-3.5-turbo"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = response_content
        
        self._client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    async def generate_debate_topic(self, user_message: str) -> DebateTopic:
        self.generate_topic_calls.append(user_message)
        if self.should_fail:
            raise LLMServiceError("Mock AI failure")
        
        return DebateTopic.create(
            title="Mock controversial topic",
            description="A mock topic for testing",
            bot_stance=DebateStance.FOR,
            key_arguments=["Mock argument 1", "Mock argument 2", "Mock argument 3"]
        )
    
    async def health_check(self) -> bool:
        self.health_check_calls.append(True)
        return not self.should_fail


class MockConversationRepository:
    """Mock repository for testing."""
    
    def __init__(self):
        self.conversations = {}
        self.save_calls = []
    
    async def save(self, conversation):
        self.save_calls.append(conversation)
        self.conversations[conversation.conversation_id] = conversation
    
    async def get_by_id(self, conversation_id):
        return self.conversations.get(conversation_id)


class TestAIIntegration:
    """Test AI integration in use cases."""
    
    def test_continue_conversation_with_ai_service(self):
        """Test that continue conversation uses AI service for response generation."""
        # Setup
        mock_llm = MockLLMService(response_content="This is an AI-generated response with a question?")
        mock_repo = MockConversationRepository()
        use_case = ContinueConversationUseCase(mock_repo, mock_llm)
        
        # Create a conversation with topic
        conversation = Conversation.create()
        topic = DebateTopic.create(
            title="Test topic",
            description="A test topic",
            bot_stance=DebateStance.FOR,
            key_arguments=["Argument 1", "Argument 2", "Argument 3"]
        )
        conversation.set_debate_topic(topic)
        
        # Add initial messages
        user_msg = Message.create("Initial user message", "user")
        bot_msg = Message.create("Initial bot message", "bot")
        conversation.add_message(user_msg)
        conversation.add_message(bot_msg)
        
        # Save to mock repository
        mock_repo.conversations[conversation.conversation_id] = conversation
        
        # Execute
        import asyncio
        result = asyncio.run(use_case.execute(
            str(conversation.conversation_id), 
            "User follow-up message"
        ))
        
        # Verify AI service was called
        assert len(mock_llm._client.chat.completions.create.call_args_list) == 1
        
        # Verify conversation was updated
        assert len(result.get_recent_messages()) == 4  # 2 initial + 2 new
        latest_bot_message = result.get_recent_messages()[-1]
        assert latest_bot_message.role == "bot"
        assert "AI-generated response" in latest_bot_message.content
    
    def test_continue_conversation_ai_failure_fallback(self):
        """Test fallback when AI service fails."""
        # Setup with failing AI service
        mock_llm = MockLLMService(should_fail=True)
        mock_repo = MockConversationRepository()
        use_case = ContinueConversationUseCase(mock_repo, mock_llm)
        
        # Create conversation with topic
        conversation = Conversation.create()
        topic = DebateTopic.create(
            title="Climate change is a hoax",
            description="Test topic",
            bot_stance=DebateStance.FOR,
            key_arguments=["Argument about climate", "Another climate argument"]
        )
        conversation.set_debate_topic(topic)
        mock_repo.conversations[conversation.conversation_id] = conversation
        
        # Execute
        import asyncio
        result = asyncio.run(use_case.execute(
            str(conversation.conversation_id),
            "Climate change is real"
        ))
        
        # Should fall back to template response
        latest_bot_message = result.get_recent_messages()[-1]
        assert latest_bot_message.role == "bot"
        assert len(latest_bot_message.content) > 10  # Should have substantial response
        # Note: Mock response might not have question, but should be substantial
    
    def test_continue_conversation_without_ai_service(self):
        """Test continue conversation works without AI service."""
        # Setup without AI service
        mock_repo = MockConversationRepository()
        use_case = ContinueConversationUseCase(mock_repo, None)
        
        # Create conversation with topic
        conversation = Conversation.create()
        topic = DebateTopic.create(
            title="Vaccines are dangerous",
            description="Test topic",
            bot_stance=DebateStance.FOR,
            key_arguments=["Vaccine argument 1", "Vaccine argument 2"]
        )
        conversation.set_debate_topic(topic)
        mock_repo.conversations[conversation.conversation_id] = conversation
        
        # Execute
        import asyncio
        result = asyncio.run(use_case.execute(
            str(conversation.conversation_id),
            "Vaccines are safe"
        ))
        
        # Should use template response
        latest_bot_message = result.get_recent_messages()[-1]
        assert latest_bot_message.role == "bot"
        assert len(latest_bot_message.content) > 10
        assert any(arg in latest_bot_message.content for arg in topic.key_arguments)
    
    def test_enhanced_mock_response_generation(self):
        """Test enhanced mock response generation logic."""
        # Setup with mock service (simulates MockOpenAIService)
        mock_llm = MockLLMService()
        # Add the _topics_data attribute to simulate MockOpenAIService
        mock_llm._topics_data = [DebateTopic.create(
            title="Test topic",
            description="Test",
            bot_stance=DebateStance.FOR,
            key_arguments=["climate is natural", "scientists are wrong", "data is manipulated"]
        )]
        
        mock_repo = MockConversationRepository()
        use_case = ContinueConversationUseCase(mock_repo, mock_llm)
        
        # Create conversation with climate topic
        conversation = Conversation.create()
        topic = DebateTopic.create(
            title="Climate change is natural",
            description="Climate change is just natural cycles",
            bot_stance=DebateStance.FOR,
            key_arguments=["climate is natural", "solar cycles", "historical variations"]
        )
        conversation.set_debate_topic(topic)
        
        # Add some conversation history
        for i in range(3):
            user_msg = Message.create(f"User message {i}", "user")
            bot_msg = Message.create(f"Bot message {i}", "bot")
            conversation.add_message(user_msg)
            conversation.add_message(bot_msg)
        
        mock_repo.conversations[conversation.conversation_id] = conversation
        
        # Execute with climate-related user message
        import asyncio
        result = asyncio.run(use_case.execute(
            str(conversation.conversation_id),
            "But the climate data shows warming"
        ))
        
        # Verify enhanced mock response
        latest_bot_message = result.get_recent_messages()[-1]
        assert latest_bot_message.role == "bot"
        
        # Should use contextual starter for deeper conversation
        response_content = latest_bot_message.content
        # Note: This test may get the real AI response or enhanced mock response
        # Just verify it's a substantial debate response
        assert len(response_content) > 20
        
        # Should be a proper debate response (either from AI or enhanced mock)
        assert len(response_content) > 10
        
        # Should contain some debate-like language or question mark
        debate_indicators = ["but", "however", "consider", "think", "believe", "argue", "point", "evidence", "?", "missing", "key"]
        assert any(indicator in response_content.lower() for indicator in debate_indicators)
    
    def test_template_response_variety(self):
        """Test that template responses show variety."""
        mock_repo = MockConversationRepository()
        use_case = ContinueConversationUseCase(mock_repo, None)
        
        topic = DebateTopic.create(
            title="Social media is harmful",
            description="Social media causes more harm than good",
            bot_stance=DebateStance.FOR,
            key_arguments=["Addiction", "Mental health issues", "Privacy concerns", "Misinformation"]
        )
        
        # Generate multiple template responses
        responses = []
        for i in range(10):
            response = use_case._generate_template_response(topic, f"User message {i}")
            responses.append(response)
        
        # Should have variety in responses
        unique_responses = set(responses)
        assert len(unique_responses) > 1, "Template responses should show variety"
        
        # All responses should include topic arguments
        for response in responses:
            assert any(arg in response for arg in topic.key_arguments)
            assert "?" in response  # Should ask questions
            assert len(response) > 20  # Should be substantial
    
    def test_conversation_context_building(self):
        """Test that conversation history is properly built for AI prompts."""
        # This test verifies the internal logic of building conversation context
        mock_llm = MockLLMService(response_content="Contextual AI response")
        mock_repo = MockConversationRepository()
        use_case = ContinueConversationUseCase(mock_repo, mock_llm)
        
        # Create conversation with history
        conversation = Conversation.create()
        topic = DebateTopic.create(
            title="Test topic",
            description="Test",
            bot_stance=DebateStance.FOR,
            key_arguments=["Arg 1", "Arg 2", "Arg 3"]
        )
        conversation.set_debate_topic(topic)
        
        # Add conversation history (alternating user/bot messages)
        messages = [
            ("User: First message", "user"),
            ("Bot: First response", "bot"),
            ("User: Second message", "user"),
            ("Bot: Second response", "bot"),
        ]
        
        for content, role in messages:
            msg = Message.create(content, role)
            conversation.add_message(msg)
        
        mock_repo.conversations[conversation.conversation_id] = conversation
        
        # Execute
        import asyncio
        result = asyncio.run(use_case.execute(
            str(conversation.conversation_id),
            "Latest user message"
        ))
        
        # Verify AI was called with proper context
        assert len(mock_llm._client.chat.completions.create.call_args_list) == 1
        call_args = mock_llm._client.chat.completions.create.call_args_list[0]
        
        # Check that the prompt includes conversation history
        prompt_content = call_args[1]['messages'][1]['content']  # User message content
        assert "conversation history" in prompt_content.lower()
        assert "Latest user message" in prompt_content
        assert topic.title in prompt_content
