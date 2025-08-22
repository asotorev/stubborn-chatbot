"""API response schemas."""

from typing import List
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Schema for individual messages in conversation history."""
    
    role: str = Field(
        ...,
        description="Role of the message sender ('user' or 'bot')"
    )
    message: str = Field(
        ...,
        description="Content of the message"
    )


class ConversationResponse(BaseModel):
    """Schema for conversation API responses."""
    
    conversation_id: str = Field(
        ...,
        description="ID of the conversation"
    )
    messages: List[MessageResponse] = Field(
        ...,
        description="History of the 5 most recent messages, most recent last"
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(
        ...,
        description="Error message"
    )
    detail: str = Field(
        ...,
        description="Detailed error information"
    )


class HealthResponse(BaseModel):
    """Schema for health check responses."""
    
    status: str = Field(
        ...,
        description="Health status"
    )
    version: str = Field(
        ...,
        description="API version"
    )
