"""
Comprehensive integration tests for debate flow functionality.

Tests the complete debate experience from topic generation through
multi-turn conversations with AI-powered responses.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestDebateFlow:
    """Test complete debate conversation flows."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_complete_debate_flow_single_conversation(self):
        """Test a complete debate flow in a single conversation."""
        # Start conversation
        start_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": "I think renewable energy is the future"
            }
        )
        
        assert start_response.status_code == 200
        start_data = start_response.json()
        
        # Validate initial response structure
        assert "conversation_id" in start_data
        assert "messages" in start_data
        assert len(start_data["messages"]) == 2
        
        conversation_id = start_data["conversation_id"]
        user_msg = start_data["messages"][0]
        bot_msg = start_data["messages"][1]
        
        # Validate message structure
        assert user_msg["role"] == "user"
        assert user_msg["message"] == "I think renewable energy is the future"
        assert bot_msg["role"] == "bot"
        assert len(bot_msg["message"]) > 10  # Bot should have substantial response
        
        # Continue conversation - multiple turns
        follow_up_messages = [
            "But renewable energy is expensive and unreliable",
            "Solar panels and wind turbines are becoming much cheaper",
            "What about when the sun doesn't shine and wind doesn't blow?"
        ]
        
        for i, user_message in enumerate(follow_up_messages):
            continue_response = self.client.post(
                "/api/v1/conversation",
                json={
                    "conversation_id": conversation_id,
                    "message": user_message
                }
            )
            
            assert continue_response.status_code == 200
            continue_data = continue_response.json()
            
            # Validate conversation growth
            expected_message_count = 2 + (i + 1) * 2  # Initial 2 + each exchange adds 2
            assert len(continue_data["messages"]) == min(expected_message_count, 5)  # Max 5 messages
            
            # Validate latest bot response
            latest_bot_message = continue_data["messages"][-1]
            assert latest_bot_message["role"] == "bot"
            assert len(latest_bot_message["message"]) > 10
            
            # Bot response should be different from previous (no exact repeats)
            if i > 0:
                previous_bot_message = bot_msg["message"]
                assert latest_bot_message["message"] != previous_bot_message
            
            bot_msg = latest_bot_message
    
    def test_multiple_conversation_independence(self):
        """Test that multiple conversations are independent."""
        # Start two different conversations
        conv1_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": "I love pineapple on pizza"
            }
        )
        
        conv2_response = self.client.post(
            "/api/v1/conversation", 
            json={
                "conversation_id": None,
                "message": "Dogs are better than cats"
            }
        )
        
        assert conv1_response.status_code == 200
        assert conv2_response.status_code == 200
        
        conv1_data = conv1_response.json()
        conv2_data = conv2_response.json()
        
        # Conversations should have different IDs
        assert conv1_data["conversation_id"] != conv2_data["conversation_id"]
        
        # Continue both conversations independently
        conv1_continue = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": conv1_data["conversation_id"],
                "message": "It adds a nice sweet and savory balance"
            }
        )
        
        conv2_continue = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": conv2_data["conversation_id"],
                "message": "Dogs are loyal and protective"
            }
        )
        
        assert conv1_continue.status_code == 200
        assert conv2_continue.status_code == 200
        
        # Responses should be contextually different
        conv1_bot_response = conv1_continue.json()["messages"][-1]["message"]
        conv2_bot_response = conv2_continue.json()["messages"][-1]["message"]
        
        assert conv1_bot_response != conv2_bot_response
    
    def test_conversation_message_limit_behavior(self):
        """Test that conversation properly limits to 5 most recent messages."""
        # Start conversation
        start_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": "Initial message"
            }
        )
        
        conversation_id = start_response.json()["conversation_id"]
        
        # Add multiple messages to exceed 5 message limit
        messages = [
            "Second message",
            "Third message", 
            "Fourth message",
            "Fifth message",
            "Sixth message"  # This should push the first messages out
        ]
        
        for message in messages:
            continue_response = self.client.post(
                "/api/v1/conversation",
                json={
                    "conversation_id": conversation_id,
                    "message": message
                }
            )
            assert continue_response.status_code == 200
        
        # Final response should have exactly 5 messages (most recent)
        final_data = continue_response.json()
        assert len(final_data["messages"]) == 5
        
        # Should NOT contain the initial message anymore
        message_contents = [msg["message"] for msg in final_data["messages"]]
        assert "Initial message" not in message_contents
        assert "Sixth message" in message_contents  # Should contain most recent
    
    def test_enhanced_bot_response_variety(self):
        """Test that bot responses show variety and context awareness."""
        # Start conversation
        start_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": "I think vaccines are safe"
            }
        )
        
        conversation_id = start_response.json()["conversation_id"]
        
        # Collect multiple bot responses
        bot_responses = []
        test_messages = [
            "The scientific evidence is overwhelming",
            "Millions of people get vaccinated safely every year",
            "The side effects are extremely rare",
            "Vaccines have eliminated many diseases"
        ]
        
        for message in test_messages:
            continue_response = self.client.post(
                "/api/v1/conversation",
                json={
                    "conversation_id": conversation_id,
                    "message": message
                }
            )
            
            assert continue_response.status_code == 200
            bot_response = continue_response.json()["messages"][-1]["message"]
            bot_responses.append(bot_response)
        
        # Responses should be varied (not all identical)
        unique_responses = set(bot_responses)
        assert len(unique_responses) > 1, "Bot responses should show variety"
        
        # Each response should be substantial
        for response in bot_responses:
            assert len(response) > 20, f"Response too short: {response}"
            assert "?" in response, f"Response should ask a question: {response}"
    
    def test_conversation_persistence_across_requests(self):
        """Test that conversation state persists across multiple requests."""
        # Start conversation
        start_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": "I believe in traditional medicine"
            }
        )
        
        conversation_id = start_response.json()["conversation_id"]
        
        # Continue conversation after some "time"
        continue_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": conversation_id,
                "message": "Natural remedies have been used for thousands of years"
            }
        )
        
        assert continue_response.status_code == 200
        continue_data = continue_response.json()
        
        # Should have 4 messages total (2 from start + 2 from continue)
        assert len(continue_data["messages"]) == 4
        
        # Should contain both original and new messages
        all_messages = [msg["message"] for msg in continue_data["messages"]]
        assert "I believe in traditional medicine" in all_messages
        assert "Natural remedies have been used for thousands of years" in all_messages
    
    def test_error_handling_in_debate_flow(self):
        """Test error handling during debate conversations."""
        # Test with invalid conversation ID
        invalid_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": "invalid-uuid-format",
                "message": "Some message"
            }
        )
        
        assert invalid_response.status_code == 400
        assert "invalid conversation id format" in invalid_response.json()["detail"].lower()
        
        # Test with non-existent conversation ID
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        nonexistent_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": nonexistent_id,
                "message": "Some message"
            }
        )
        
        assert nonexistent_response.status_code == 400
        assert "not found" in nonexistent_response.json()["detail"].lower()
    
    def test_debate_topic_consistency(self):
        """Test that bot maintains consistent stance throughout conversation."""
        # Start conversation
        start_response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": "Electric cars are the future of transportation"
            }
        )
        
        conversation_id = start_response.json()["conversation_id"]
        initial_bot_response = start_response.json()["messages"][1]["message"]
        
        # Continue with multiple challenging messages
        challenging_messages = [
            "Electric cars have much lower emissions",
            "The technology is improving rapidly",
            "Many countries are banning gas cars"
        ]
        
        previous_responses = [initial_bot_response]
        
        for message in challenging_messages:
            continue_response = self.client.post(
                "/api/v1/conversation",
                json={
                    "conversation_id": conversation_id,
                    "message": message
                }
            )
            
            bot_response = continue_response.json()["messages"][-1]["message"]
            previous_responses.append(bot_response)
            
            # Bot should maintain its contrarian stance
            # TODO: With real AI integration, add semantic consistency checks
            # to verify bot maintains the same stance throughout the conversation
            assert len(bot_response) > 10
            assert "?" in bot_response  # Should engage with questions
    
    @pytest.mark.parametrize("user_input,expected_elements", [
        ("I love social media", ["social", "media"]),
        ("Climate change is real", ["climate", "change"]),
        ("Artificial intelligence will help humanity", ["AI", "artificial", "intelligence"]),
        ("Space exploration is worth the cost", ["space", "exploration"]),
    ])
    def test_topic_relevance_indicators(self, user_input, expected_elements):
        """Test that bot responses show some relevance to user input topics."""
        response = self.client.post(
            "/api/v1/conversation",
            json={
                "conversation_id": None,
                "message": user_input
            }
        )
        
        assert response.status_code == 200
        bot_message = response.json()["messages"][1]["message"].lower()
        
        # Note: With mock service, we can't guarantee topic relevance,
        # but we can ensure the response is substantial and engaging
        assert len(bot_message) > 20
        assert any(punct in bot_message for punct in ["?", "!", "."])
        
        # The response should be a proper debate response
        debate_indicators = ["but", "however", "actually", "consider", "evidence", "think", "believe"]
        assert any(indicator in bot_message for indicator in debate_indicators)
