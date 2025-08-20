"""Dependency injection container."""

from functools import lru_cache
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface
from src.infrastructure.repositories.conversation_memory import ConversationMemoryRepository
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase
from src.core.domain_services.topic_service import TopicService


@lru_cache()
def get_conversation_repository() -> ConversationRepositoryInterface:
    """Get conversation repository dependency."""
    return ConversationMemoryRepository()


@lru_cache()
def get_topic_service() -> TopicService:
    """Get topic service dependency."""
    # TODO: Integrate with OpenAI service for dynamic topic generation
    return TopicService(llm_service=None)


def get_start_conversation_use_case() -> StartConversationUseCase:
    """Get start conversation use case dependency."""
    return StartConversationUseCase(
        conversation_repository=get_conversation_repository(),
        topic_service=get_topic_service()
    )


def get_continue_conversation_use_case() -> ContinueConversationUseCase:
    """Get continue conversation use case dependency."""
    return ContinueConversationUseCase(
        conversation_repository=get_conversation_repository()
    )
