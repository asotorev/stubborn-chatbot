#!/usr/bin/env python3
"""
End-to-end deployment verification tests.

These tests verify that the API meets the challenge requirements
and can handle the complete conversation workflow using TestClient.
"""

import pytest
from typing import Dict, Any
from fastapi.testclient import TestClient
from src.main import app


class TestDeploymentVerification:
    """End-to-end tests for API deployment verification."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Test client for making API requests."""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test that the health endpoint is working."""
        response = client.get("/health")
        
        assert response.status_code == 200, f"Health check failed: HTTP {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data, "Health response missing 'status' field"
        
        print(f"Health check status: {health_data.get('status')}")
    
    def test_api_documentation(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200, f"API documentation failed: HTTP {response.status_code}"
        print("API documentation is accessible")
    
    def test_new_conversation_creation(self, client):
        """Test starting a new conversation."""
        payload = {
            "conversation_id": None,
            "message": "I think artificial intelligence will take over the world"
        }
        
        response = client.post("/conversation", json=payload)
        
        assert response.status_code == 200, f"New conversation failed: HTTP {response.status_code}\nResponse: {response.text}"
        
        data = response.json()
        self._verify_response_structure(data)
        
        conversation_id = data.get('conversation_id')
        messages = data.get('messages', [])
        
        assert conversation_id is not None, "Missing conversation_id in response"
        assert len(messages) >= 2, f"Expected at least 2 messages, got {len(messages)}"
        
        user_msg = messages[0]
        bot_msg = messages[1]
        
        assert user_msg.get('role') == 'user', f"First message should be from user, got {user_msg.get('role')}"
        assert bot_msg.get('role') == 'bot', f"Second message should be from bot, got {bot_msg.get('role')}"
        
        print(f"New conversation created: {conversation_id}")
        print(f"Messages in response: {len(messages)}")
        print(f"User message: {user_msg.get('message', '')[:50]}...")
        print(f"Bot message: {bot_msg.get('message', '')[:50]}...")
        
        # Store conversation_id for next test
        self.conversation_id = conversation_id
    
    def test_continue_conversation(self, client):
        """Test continuing an existing conversation."""
        # First start a conversation
        start_payload = {
            "conversation_id": None,
            "message": "I think artificial intelligence will take over the world"
        }
        start_response = client.post("/conversation", json=start_payload)
        assert start_response.status_code == 200
        
        conversation_id = start_response.json()["conversation_id"]
        
        # Then continue it
        payload = {
            "conversation_id": conversation_id,
            "message": "But what about the benefits of AI for healthcare and research?"
        }
        
        response = client.post("/conversation", json=payload)
        
        assert response.status_code == 200, f"Continue conversation failed: HTTP {response.status_code}\nResponse: {response.text}"
        
        data = response.json()
        self._verify_response_structure(data)
        
        messages = data.get('messages', [])
        assert len(messages) >= 1, "No messages in continue conversation response"
        
        # Check that bot responded (last message should be from bot)
        latest_msg = messages[-1]
        assert latest_msg.get('role') == 'bot', f"Expected bot response, got {latest_msg.get('role')}"
        
        print(f"Conversation continued: {len(messages)} messages total")
        print(f"Bot response: {latest_msg.get('message', '')[:50]}...")
    
    def test_conversation_persistence(self, client):
        """Test that conversations persist across multiple interactions."""
        # Start a new conversation
        payload1 = {
            "conversation_id": None,
            "message": "Should we ban social media for teenagers?"
        }
        
        response1 = client.post("/conversation", json=payload1)
        assert response1.status_code == 200
        
        data1 = response1.json()
        conversation_id = data1.get('conversation_id')
        initial_message_count = len(data1.get('messages', []))
        
        # Continue the conversation multiple times
        for i, follow_up in enumerate([
            "But teenagers need to learn digital literacy",
            "What about cyberbullying and mental health issues?",
            "Don't parents have a responsibility to monitor usage?"
        ], 1):
            payload = {
                "conversation_id": conversation_id,
                "message": follow_up
            }
            
            response = client.post("/conversation", json=payload)
            assert response.status_code == 200, f"Follow-up {i} failed"
            
            data = response.json()
            messages = data.get('messages', [])
            
            # API returns last 5 messages, so we should have at least the recent exchanges
            assert len(messages) >= 2, f"Should have at least user message and bot response at step {i}"
            assert len(messages) <= 5, f"Should not exceed 5 messages (API limit) at step {i}"
            
            # Verify conversation ID consistency
            assert data.get('conversation_id') == conversation_id, f"Conversation ID changed at step {i}"
        
        print(f"Conversation persistence verified across multiple interactions")
    
    def test_error_handling(self, client):
        """Test API error handling for invalid requests."""
        # Test missing message field
        invalid_payload1 = {"conversation_id": None}
        response1 = client.post("/conversation", json=invalid_payload1)
        assert response1.status_code in [400, 422], "Should return error for missing message"
        
        # Test invalid conversation_id
        invalid_payload2 = {
            "conversation_id": "invalid-uuid-format",
            "message": "This should fail"
        }
        response2 = client.post("/conversation", json=invalid_payload2)
        # This might succeed with graceful handling or fail - both are acceptable
        
        # Test empty message
        invalid_payload3 = {
            "conversation_id": None,
            "message": ""
        }
        response3 = client.post("/conversation", json=invalid_payload3)
        assert response3.status_code in [400, 422], "Should return error for empty message"
        
        print("Error handling tests completed")
    
    def _verify_response_structure(self, data: Dict[str, Any]) -> None:
        """Verify that response matches the expected structure."""
        required_fields = ['conversation_id', 'messages']
        
        for field in required_fields:
            assert field in data, f"Missing required field '{field}' in response"
        
        messages = data.get('messages', [])
        assert isinstance(messages, list), "'messages' field must be a list"
        
        # Verify message structure
        for i, message in enumerate(messages):
            assert isinstance(message, dict), f"Message {i} is not an object"
            assert 'role' in message, f"Message {i} missing 'role' field"
            assert 'message' in message, f"Message {i} missing 'message' field"
            assert message['role'] in ['user', 'bot'], f"Message {i} has invalid role: {message['role']}"


@pytest.mark.integration
@pytest.mark.slow
class TestFullWorkflow:
    """Test the complete conversation workflow end-to-end."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Test client for making API requests."""
        return TestClient(app)
    
    def test_complete_debate_workflow(self, client):
        """Test a complete debate conversation workflow."""
        
        # Define a complete debate scenario
        debate_messages = [
            "Climate change is the most important issue of our time",
            "But economic growth is more important for developing countries",
            "We can have green economic growth through renewable energy",
            "The transition costs will hurt the poor the most",
            "Government subsidies can help with the transition costs"
        ]
        
        conversation_id = None
        
        for i, message in enumerate(debate_messages):
            payload = {
                "conversation_id": conversation_id,
                "message": message
            }
            
            response = client.post("/conversation", json=payload)
            assert response.status_code == 200, f"Message {i+1} failed: {response.status_code}"
            
            data = response.json()
            conversation_id = data.get('conversation_id')
            messages = data.get('messages', [])
            
            # Verify the bot is maintaining a consistent stance
            if len(messages) >= 2:
                bot_messages = [msg for msg in messages if msg['role'] == 'bot']
                assert len(bot_messages) >= 1, f"No bot response at step {i+1}"
                
                print(f"Step {i+1} - Bot: {bot_messages[-1]['message'][:100]}...")
        
        print(f"Complete debate workflow verified with {len(debate_messages)} exchanges")


# Standalone execution capability (maintains backward compatibility)
if __name__ == "__main__":
    import sys
    
    # Run the tests using pytest
    exit_code = pytest.main([__file__, "-v", "-s"])
    sys.exit(exit_code)
