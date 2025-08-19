"""
Domain services for business logic.

Contains business logic that doesn't naturally fit within a single entity
but operates on domain objects.
"""

from .topic_service import TopicService

__all__ = ["TopicService"]
