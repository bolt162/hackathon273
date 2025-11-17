"""
Redis service for state management, caching, and vector search
"""
import redis
import json
from typing import Dict, List, Optional, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.client = None
        self.connect()

    def connect(self):
        """Connect to Redis Stack"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            self.client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def set_state(self, key: str, value: Any, expire: Optional[int] = None):
        """Set a state value in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if expire:
                self.client.setex(key, expire, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Error setting state {key}: {e}")
            return False

    def get_state(self, key: str) -> Optional[Any]:
        """Get a state value from Redis"""
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting state {key}: {e}")
            return None

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter"""
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing {key}: {e}")
            return 0

    def set_hash(self, name: str, mapping: Dict):
        """Set hash fields"""
        try:
            self.client.hset(name, mapping=mapping)
            return True
        except Exception as e:
            logger.error(f"Error setting hash {name}: {e}")
            return False

    def get_hash(self, name: str) -> Optional[Dict]:
        """Get all hash fields"""
        try:
            return self.client.hgetall(name)
        except Exception as e:
            logger.error(f"Error getting hash {name}: {e}")
            return None

    def get_hash_field(self, name: str, field: str) -> Optional[str]:
        """Get a specific hash field"""
        try:
            return self.client.hget(name, field)
        except Exception as e:
            logger.error(f"Error getting hash field {name}.{field}: {e}")
            return None

    def store_embedding(self, key: str, embedding: List[float], metadata: Dict):
        """Store an embedding with metadata"""
        try:
            data = {
                "embedding": json.dumps(embedding),
                "metadata": json.dumps(metadata)
            }
            return self.set_hash(f"embedding:{key}", data)
        except Exception as e:
            logger.error(f"Error storing embedding {key}: {e}")
            return False

    def get_embedding(self, key: str) -> Optional[Dict]:
        """Get an embedding with metadata"""
        try:
            data = self.get_hash(f"embedding:{key}")
            if data:
                return {
                    "embedding": json.loads(data.get("embedding", "[]")),
                    "metadata": json.loads(data.get("metadata", "{}"))
                }
            return None
        except Exception as e:
            logger.error(f"Error getting embedding {key}: {e}")
            return None

    def search_embeddings(self, query_embedding: List[float], top_k: int = 10) -> List[Dict]:
        """
        Search for similar embeddings
        Note: This is a simple implementation. For production, use RedisSearch with vector similarity
        """
        try:
            # Get all embedding keys
            keys = self.client.keys("embedding:*")
            results = []

            for key in keys[:100]:  # Limit to first 100 for performance
                embedding_data = self.get_embedding(key.replace("embedding:", ""))
                if embedding_data:
                    # Simple cosine similarity (for demo purposes)
                    similarity = self._cosine_similarity(query_embedding, embedding_data["embedding"])
                    results.append({
                        "key": key.replace("embedding:", ""),
                        "similarity": similarity,
                        "metadata": embedding_data["metadata"]
                    })

            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            if magnitude1 == 0 or magnitude2 == 0:
                return 0
            return dot_product / (magnitude1 * magnitude2)
        except:
            return 0

    def publish(self, channel: str, message: str):
        """Publish a message to a channel"""
        try:
            self.client.publish(channel, message)
            return True
        except Exception as e:
            logger.error(f"Error publishing to {channel}: {e}")
            return False

    def subscribe(self, channels: List[str]):
        """Subscribe to channels"""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            logger.error(f"Error subscribing to channels: {e}")
            return None

    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching a pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            return []

    def delete(self, key: str):
        """Delete a key"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False

    def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            return self.client.ping()
        except:
            return False


# Singleton instance
redis_service = RedisService()
