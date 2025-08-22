"""End-to-end API tests."""

import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestConversationAPI:
    """Test the conversation API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"

    def test_start_conversation_success(self):
        """Test starting a new conversation via API."""
        response = self.client.post(
            "/conversation",
            json={
                "conversation_id": None,
                "message": "I think climate change is real"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "conversation_id" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == 2  # User message + bot response
        
        # Validate message structure
        user_msg = data["messages"][0]
        bot_msg = data["messages"][1]
        
        assert user_msg["role"] == "user"
        assert user_msg["message"] == "I think climate change is real"
        assert bot_msg["role"] == "bot"
        assert len(bot_msg["message"]) > 0

    def test_continue_conversation_success(self):
        """Test continuing an existing conversation via API."""
        # First, start a conversation
        start_response = self.client.post(
            "/conversation",
            json={
                "conversation_id": None,
                "message": "Initial message"
            }
        )
        
        assert start_response.status_code == 200
        conversation_id = start_response.json()["conversation_id"]
        
        # Then continue it
        continue_response = self.client.post(
            "/conversation",
            json={
                "conversation_id": conversation_id,
                "message": "Follow-up message"
            }
        )
        
        assert continue_response.status_code == 200
        data = continue_response.json()
        
        # Should have same conversation_id
        assert data["conversation_id"] == conversation_id
        
        # Should have 4 messages now (2 from start + 2 from continue)
        assert len(data["messages"]) == 4
        
        # Last message should be the follow-up
        assert data["messages"][-2]["message"] == "Follow-up message"
        assert data["messages"][-2]["role"] == "user"
        assert data["messages"][-1]["role"] == "bot"

    def test_start_conversation_empty_message(self):
        """Test starting conversation with empty message fails."""
        response = self.client.post(
            "/conversation",
            json={
                "conversation_id": None,
                "message": ""
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_continue_conversation_not_found(self):
        """Test continuing non-existent conversation fails."""
        response = self.client.post(
            "/conversation",
            json={
                "conversation_id": "non-existent-id",
                "message": "Some message"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "invalid conversation id format" in data["detail"].lower()

    def test_invalid_request_format(self):
        """Test invalid request format returns 422."""
        response = self.client.post(
            "/conversation",
            json={
                "invalid_field": "value"
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error

    def test_conversation_message_limit(self):
        """Test that API returns maximum 5 recent messages."""
        # Start conversation
        start_response = self.client.post(
            "/conversation",
            json={"conversation_id": None, "message": "Message 1"}
        )
        conversation_id = start_response.json()["conversation_id"]
        
        # Add multiple messages to exceed 5 total
        for i in range(2, 6):  # Messages 2, 3, 4, 5
            self.client.post(
                "/conversation",
                json={"conversation_id": conversation_id, "message": f"Message {i}"}
            )
        
        # Get final response
        final_response = self.client.post(
            "/conversation",
            json={"conversation_id": conversation_id, "message": "Final message"}
        )
        
        data = final_response.json()
        
        # Should only return 5 most recent messages
        assert len(data["messages"]) == 5
        
        # Should include the final message
        assert any(msg["message"] == "Final message" for msg in data["messages"])
