"""
LLM service interface for AI-powered topic generation.

Defines the contract for generating debate topics and stances
using Large Language Models.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.debate_topic import DebateTopic


class LLMServiceInterface(ABC):
    """
    Abstract interface for LLM-powered topic analysis and generation.
    
    This interface allows the domain layer to request AI-generated
    debate topics without depending on specific LLM implementations.
    """
    
    @abstractmethod
    async def generate_debate_topic(self, user_message: str) -> DebateTopic:
        """
        Generate a debate topic and controversial stance based on user input.
        
        Analyzes the user's message to identify the main topic, then generates
        a controversial opposing stance that the bot can argue for.
        
        Args:
            user_message: The user's input message to analyze
            
        Returns:
            A DebateTopic with a controversial stance for the bot to defend
            
        Raises:
            LLMServiceError: If topic generation fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM service is available and responding.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        pass


class LLMServiceError(Exception):
    """
    Exception raised when LLM service operations fail.
    
    This could be due to API failures, network issues, content policy
    violations, or other LLM-related problems.
    """
    
    def __init__(self, message: str, cause: Exception | None = None):
        """
        Initialize an LLM service error.
        
        Args:
            message: Human-readable error description
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.cause = cause
