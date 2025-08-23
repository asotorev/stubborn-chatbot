"""
Abstract interfaces and ports for the core domain.

These define the contracts that outer layers must implement,
following the Dependency Inversion Principle.
"""

from .conversation_repository import ConversationRepositoryInterface
from .llm_service import LLMServiceInterface

__all__ = ["ConversationRepositoryInterface", "LLMServiceInterface"]
