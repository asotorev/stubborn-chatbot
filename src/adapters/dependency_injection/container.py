"""Dependency injection container."""

from functools import lru_cache
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface
from src.infrastructure.repositories.conversation_memory import InMemoryConversationRepository
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase


@lru_cache()
def get_conversation_repository() -> ConversationRepositoryInterface:
    """Get conversation repository dependency."""
    return InMemoryConversationRepository()


def get_start_conversation_use_case() -> StartConversationUseCase:
    """Get start conversation use case dependency."""
    return StartConversationUseCase(
        conversation_repository=get_conversation_repository()
    )


def get_continue_conversation_use_case() -> ContinueConversationUseCase:
    """Get continue conversation use case dependency."""
    return ContinueConversationUseCase(
        conversation_repository=get_conversation_repository()
    )
