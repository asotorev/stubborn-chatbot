"""Application settings and configuration."""

import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        # Load .env file if present
        self._load_env_file()
        
        # OpenAI Configuration
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Redis Configuration
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
        self.redis_db: int = int(os.getenv("REDIS_DB", "0"))
        self.redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
        self.redis_retry_on_timeout: bool = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
        
        # Storage Configuration
        self.storage_type: str = os.getenv("STORAGE_TYPE", "memory")  # "memory" or "redis"
        
        # Application Configuration
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Development flags
        self.use_mock_openai: bool = os.getenv("USE_MOCK_OPENAI", "false").lower() == "true"
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # python-dotenv not installed, skip loading .env file
            pass
    
    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key and self.openai_api_key.strip() != "your_openai_api_key_here")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
