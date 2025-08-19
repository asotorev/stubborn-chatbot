"""Conversation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from src.adapters.api.schemas.requests import ConversationRequest
from src.adapters.api.schemas.responses import ConversationResponse, ErrorResponse, MessageResponse
from src.adapters.dependency_injection.container import (
    get_start_conversation_use_case,
    get_continue_conversation_use_case
)
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase


router = APIRouter(prefix="/api/v1", tags=["Conversation"])


@router.post(
    "/conversation",
    response_model=ConversationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def handle_conversation(
    request: ConversationRequest,
    start_use_case: StartConversationUseCase = Depends(get_start_conversation_use_case),
    continue_use_case: ContinueConversationUseCase = Depends(get_continue_conversation_use_case)
) -> ConversationResponse:
    """Handle conversation requests."""
    try:
        if request.conversation_id is None:
            # Start new conversation
            conversation = start_use_case.execute(request.message)
        else:
            # Continue existing conversation
            conversation = continue_use_case.execute(request.conversation_id, request.message)
        
        # Convert to response format (last 5 messages, most recent last)
        recent_messages = conversation.get_recent_messages(limit=5)
        message_responses = [
            MessageResponse(
                role="user" if msg.is_from_user else "bot",
                message=msg.content
            )
            for msg in recent_messages
        ]
        
        return ConversationResponse(
            conversation_id=conversation.id,
            messages=message_responses
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
