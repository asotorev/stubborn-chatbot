"""
Redis implementation of conversation repository.

Provides persistent storage for conversations using Redis as the backend.
Includes conversation serialization and connection management.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from ...core.entities.conversation import Conversation
from ...core.entities.message import Message
from ...core.entities.debate_topic import DebateTopic, StanceType
from ...core.interfaces.conversation_repository import ConversationRepositoryInterface, RepositoryError

logger = logging.getLogger(__name__)


class RedisConversationRepository(ConversationRepositoryInterface):
    """
    Redis implementation of conversation repository.
    
    Stores conversations as JSON documents in Redis with proper serialization
    and deserialization of conversation entities.
    """
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize the Redis conversation repository.
        
        Args:
            redis_client: Configured Redis client instance
        """
        self._redis = redis_client
        self._key_prefix = "conversation:"
    
    async def save(self, conversation: Conversation) -> None:
        """
        Save a conversation to Redis.
        
        Args:
            conversation: The conversation to save
            
        Raises:
            RepositoryError: If the save operation fails
        """
        try:
            if not isinstance(conversation, Conversation):
                raise RepositoryError("Invalid conversation object")
            
            # Serialize conversation to JSON
            conversation_data = self._serialize_conversation(conversation)
            conversation_json = json.dumps(conversation_data)
            
            # Store in Redis with key: conversation:{uuid}
            key = f"{self._key_prefix}{conversation.conversation_id}"
            await self._redis.set(key, conversation_json)
            
            logger.debug(f"Saved conversation {conversation.conversation_id} to Redis")
            
        except RedisError as e:
            error_msg = f"Failed to save conversation to Redis: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except Exception as e:
            error_msg = f"Failed to save conversation: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
    
    async def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID from Redis.
        
        Args:
            conversation_id: The unique identifier of the conversation
            
        Returns:
            The conversation if found, None otherwise
            
        Raises:
            RepositoryError: If the retrieval operation fails
        """
        try:
            key = f"{self._key_prefix}{conversation_id}"
            conversation_json = await self._redis.get(key)
            
            if conversation_json is None:
                return None
            
            # Deserialize conversation from JSON
            conversation_data = json.loads(conversation_json)
            conversation = self._deserialize_conversation(conversation_data)
            
            logger.debug(f"Retrieved conversation {conversation_id} from Redis")
            return conversation
            
        except RedisError as e:
            error_msg = f"Failed to retrieve conversation from Redis: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to deserialize conversation data: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except Exception as e:
            error_msg = f"Failed to retrieve conversation: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
    
    async def delete(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation from Redis.
        
        Args:
            conversation_id: The unique identifier of the conversation to delete
            
        Returns:
            True if the conversation was deleted, False if it didn't exist
            
        Raises:
            RepositoryError: If the delete operation fails
        """
        try:
            key = f"{self._key_prefix}{conversation_id}"
            deleted_count = await self._redis.delete(key)
            
            success = deleted_count > 0
            if success:
                logger.debug(f"Deleted conversation {conversation_id} from Redis")
            else:
                logger.debug(f"Conversation {conversation_id} not found for deletion")
            
            return success
            
        except RedisError as e:
            error_msg = f"Failed to delete conversation from Redis: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except Exception as e:
            error_msg = f"Failed to delete conversation: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
    
    async def exists(self, conversation_id: UUID) -> bool:
        """
        Check if a conversation exists in Redis.
        
        Args:
            conversation_id: The unique identifier of the conversation
            
        Returns:
            True if the conversation exists, False otherwise
            
        Raises:
            RepositoryError: If the check operation fails
        """
        try:
            key = f"{self._key_prefix}{conversation_id}"
            exists = await self._redis.exists(key)
            return bool(exists)
            
        except RedisError as e:
            error_msg = f"Failed to check conversation existence in Redis: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except Exception as e:
            error_msg = f"Failed to check conversation existence: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
    
    async def get_conversation_count(self) -> int:
        """
        Get the total number of conversations in Redis.
        
        Returns:
            Number of stored conversations
            
        Raises:
            RepositoryError: If the count operation fails
        """
        try:
            pattern = f"{self._key_prefix}*"
            keys = await self._redis.keys(pattern)
            return len(keys)
            
        except RedisError as e:
            error_msg = f"Failed to count conversations in Redis: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except Exception as e:
            error_msg = f"Failed to count conversations: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
    
    async def clear_all(self) -> None:
        """
        Clear all conversations from Redis.
        
        Warning: This will delete all conversation data permanently.
        
        Raises:
            RepositoryError: If the clear operation fails
        """
        try:
            pattern = f"{self._key_prefix}*"
            keys = await self._redis.keys(pattern)
            
            if keys:
                await self._redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} conversations from Redis")
            else:
                logger.info("No conversations to clear from Redis")
                
        except RedisError as e:
            error_msg = f"Failed to clear conversations from Redis: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
        except Exception as e:
            error_msg = f"Failed to clear conversations: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e)
    
    async def close(self) -> None:
        """
        Close the Redis connection.
        
        Should be called when the repository is no longer needed.
        """
        try:
            await self._redis.close()
            logger.debug("Closed Redis connection")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {str(e)}")
    
    def _serialize_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Serialize a conversation to a dictionary for JSON storage.
        
        Args:
            conversation: The conversation to serialize
            
        Returns:
            Dictionary representation of the conversation
        """
        # Serialize messages
        messages_data = []
        for message in conversation.get_messages():
            message_data = {
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            }
            messages_data.append(message_data)
        
        # Serialize topic
        topic_data = None
        if conversation.topic:
            topic_data = {
                "title": conversation.topic.title,
                "description": conversation.topic.description,
                "bot_stance": conversation.topic.bot_stance.value,
                "created_at": conversation.topic.created_at.isoformat()
            }
        
        # Main conversation data
        conversation_data = {
            "conversation_id": str(conversation.conversation_id),
            "created_at": conversation.created_at.isoformat(),
            "topic": topic_data,
            "messages": messages_data
        }
        
        return conversation_data
    
    def _deserialize_conversation(self, data: Dict[str, Any]) -> Conversation:
        """
        Deserialize a conversation from dictionary data.
        
        Args:
            data: Dictionary representation of the conversation
            
        Returns:
            Conversation instance
            
        Raises:
            ValueError: If the data is invalid or corrupted
        """
        try:
            # Deserialize basic fields
            conversation_id = UUID(data["conversation_id"])
            created_at = datetime.fromisoformat(data["created_at"])
            
            # Deserialize topic
            topic = None
            if data.get("topic"):
                topic_data = data["topic"]
                topic = DebateTopic(
                    title=topic_data["title"],
                    description=topic_data["description"],
                    bot_stance=StanceType(topic_data["bot_stance"]),
                    created_at=datetime.fromisoformat(topic_data["created_at"])
                )
            
            # Deserialize messages
            messages = []
            for message_data in data.get("messages", []):
                message = Message(
                    role=message_data["role"],
                    content=message_data["content"],
                    timestamp=datetime.fromisoformat(message_data["timestamp"])
                )
                messages.append(message)
            
            # Create conversation
            conversation = Conversation(
                conversation_id=conversation_id,
                topic=topic,
                created_at=created_at,
                messages=messages
            )
            
            return conversation
            
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid conversation data format: {str(e)}")


async def create_redis_client(
    redis_url: str,
    password: Optional[str] = None,
    db: int = 0,
    max_connections: int = 10,
    retry_on_timeout: bool = True
) -> redis.Redis:
    """
    Create and configure a Redis client.
    
    Args:
        redis_url: Redis connection URL (e.g., "redis://localhost:6379")
        password: Redis password (optional)
        db: Redis database number
        max_connections: Maximum number of connections in the pool
        retry_on_timeout: Whether to retry operations on timeout
        
    Returns:
        Configured Redis client
        
    Raises:
        RedisConnectionError: If connection to Redis fails
    """
    try:
        # Create connection pool
        connection_pool = redis.ConnectionPool.from_url(
            redis_url,
            password=password,
            db=db,
            max_connections=max_connections,
            retry_on_timeout=retry_on_timeout,
            decode_responses=True
        )
        
        # Create Redis client
        redis_client = redis.Redis(connection_pool=connection_pool)
        
        # Test the connection
        await redis_client.ping()
        
        logger.info(f"Successfully connected to Redis at {redis_url}")
        return redis_client
        
    except RedisError as e:
        error_msg = f"Failed to connect to Redis at {redis_url}: {str(e)}"
        logger.error(error_msg)
        raise RedisConnectionError(error_msg)
