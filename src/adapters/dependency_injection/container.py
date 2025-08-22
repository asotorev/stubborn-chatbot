"""Dependency injection container."""

import asyncio
import logging
from functools import lru_cache
from typing import Optional

from src.core.interfaces.conversation_repository import ConversationRepositoryInterface
from src.core.interfaces.llm_service import LLMServiceInterface
from src.infrastructure.repositories.conversation_memory import ConversationMemoryRepository
from src.infrastructure.repositories.redis_conversation_repository import RedisConversationRepository
from src.infrastructure.external_services.openai_service import OpenAIService, MockOpenAIService
from src.infrastructure.config import get_settings
from src.core.use_cases.start_conversation import StartConversationUseCase
from src.core.use_cases.continue_conversation import ContinueConversationUseCase
from src.core.domain_services.topic_service import TopicService

logger = logging.getLogger(__name__)


# Global Redis repository instance (cached)
_redis_repository = None


# Removed get_redis_client - using direct Redis client creation in get_redis_conversation_repository


@lru_cache()
def get_conversation_repository() -> ConversationRepositoryInterface:
    """
    Get conversation repository dependency.
    
    Returns either in-memory or Redis repository based on STORAGE_TYPE setting.
    """
    settings = get_settings()
    
    if settings.storage_type.lower() == "redis":
        return get_redis_conversation_repository()
    else:
        # Default to in-memory storage
        logger.info("Using in-memory conversation repository")
        return ConversationMemoryRepository()


def get_redis_conversation_repository() -> ConversationRepositoryInterface:
    """Get Redis conversation repository dependency."""
    global _redis_repository
    
    if _redis_repository is None:
        try:
            # Try to get Redis client synchronously first
            import redis as sync_redis
            from src.infrastructure.config import get_settings
            
            settings = get_settings()
            
            # Create synchronous Redis client for initialization
            sync_client = sync_redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True
            )
            
            # Test connection
            sync_client.ping()
            
            # Now create async Redis client
            import redis.asyncio as async_redis
            async_client = async_redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True
            )
            
            _redis_repository = RedisConversationRepository(async_client)
            logger.info("Redis conversation repository initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis repository, falling back to memory: {e}")
            return ConversationMemoryRepository()
    
    return _redis_repository


async def cleanup_redis_connections():
    """Clean up Redis connections on application shutdown."""
    global _redis_repository
    
    if _redis_repository and hasattr(_redis_repository, 'close'):
        try:
            await _redis_repository.close()
            logger.info("Redis repository connections closed")
        except Exception as e:
            logger.warning(f"Error closing Redis repository: {e}")
    
    _redis_repository = None


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
        llm_service=get_llm_service(),
        topic_service=get_topic_service()
    )
