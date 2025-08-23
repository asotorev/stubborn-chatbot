"""API request schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ConversationRequest(BaseModel):
    """Schema for conversation API requests."""
    
    conversation_id: Optional[str] = Field(
        None,
        description="ID of existing conversation. Null for new conversations."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User message to send to the chatbot"
    )
