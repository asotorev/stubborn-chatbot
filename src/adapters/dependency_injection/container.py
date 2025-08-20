"""Dependency injection container."""

from functools import lru_cache
from src.core.interfaces.conversation_repository import ConversationRepositoryInterface
from src.core.interfaces.llm_service import LLMServiceInterface
from src.infrastructure.repositories.conversation_memory import ConversationMemoryRepository
from src.infrastructure.external_services.openai_service import OpenAIService, MockOpenAIService
from src.infrastructure.config import get_settings
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase
from src.core.domain_services.topic_service import TopicService


@lru_cache()
def get_conversation_repository() -> ConversationRepositoryInterface:
    """Get conversation repository dependency."""
    return ConversationMemoryRepository()


@lru_cache()
def get_llm_service() -> LLMServiceInterface:
    """Get LLM service dependency."""
    settings = get_settings()
    
    # Use mock service if explicitly requested or if no API key is configured
    if settings.use_mock_openai or not settings.has_openai_key:
        return MockOpenAIService()
    
    # Use real OpenAI service with configured API key
    return OpenAIService(
        api_key=settings.openai_api_key,
        model=settings.openai_model
    )


@lru_cache()
def get_topic_service() -> TopicService:
    """Get topic service dependency."""
    return TopicService(llm_service=get_llm_service())


def get_start_conversation_use_case() -> StartConversationUseCase:
    """Get start conversation use case dependency."""
    return StartConversationUseCase(
        conversation_repository=get_conversation_repository(),
        topic_service=get_topic_service()
    )


def get_continue_conversation_use_case() -> ContinueConversationUseCase:
    """Get continue conversation use case dependency."""
    return ContinueConversationUseCase(
        conversation_repository=get_conversation_repository(),
        llm_service=get_llm_service()
    )
