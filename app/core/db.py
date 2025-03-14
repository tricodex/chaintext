import motor.motor_asyncio
from redis import asyncio as aioredis
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
import os
from loguru import logger

from app.core.config import settings

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

"""
Database connections and operations
"""
import sys
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from pymongo.database import Database

_MONGO_CLIENT: Optional[MongoClient] = None
_MONGO_DB: Optional[Database] = None

def init_mongodb() -> Optional[Database]:
    """Initialize MongoDB connection"""
    global _MONGO_CLIENT, _MONGO_DB
    
    if _MONGO_DB is not None:
        return _MONGO_DB
    
    # Check if we should allow operation without MongoDB
    disable_mongo = os.environ.get("DISABLE_MONGODB", "").lower() in ("true", "1", "yes")
    
    try:
        # Connect to MongoDB with timeout
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}")
        _MONGO_CLIENT = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=30000)
        
        # Check connection
        _MONGO_CLIENT.server_info()
        
        # Get database
        # Extract database name from the URI
        db_name = settings.MONGODB_URI.split("/")[-1]
        _MONGO_DB = _MONGO_CLIENT[db_name]
        logger.info(f"Connected to MongoDB database: {db_name}")
        
        return _MONGO_DB
    except (PyMongoError, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        if not disable_mongo and "test" not in sys.argv[0]:
            logger.warning("Set DISABLE_MONGODB=true in environment to run without database")
        return None

def get_mongodb() -> Optional[Database]:
    """Get MongoDB database connection"""
    global _MONGO_DB
    
    if _MONGO_DB is None:
        _MONGO_DB = init_mongodb()
        
    return _MONGO_DB

# Redis client
async def init_redis():
    try:
        redis = aioredis.from_url(settings.REDIS_URI)
        
        # Test connection
        await redis.ping()
        logger.info(f"Connected to Redis at {settings.REDIS_URI}")
        
        return redis
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

# Qdrant client
def init_qdrant():
    try:
        qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        logger.info(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        
        # Initialize vector collections
        collections = ["documentation", "blockchain_state", "social_media", "combined"]
        
        for collection in collections:
            try:
                # Check if collection exists
                qdrant_client.get_collection(collection)
                logger.info(f"Collection {collection} already exists")
            except Exception:
                # Create collection if it doesn't exist
                qdrant_client.create_collection(
                    collection_name=collection,
                    vectors_config=qdrant_models.VectorParams(
                        size=768,  # Size for Gemini embeddings
                        distance=qdrant_models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection {collection}")
        
        return qdrant_client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        raise

# Global database clients (to be initialized at startup)
mongodb = None
redis = None
qdrant_client = None

# Initialization function to be called at startup
async def init_db():
    global mongodb, redis, qdrant_client
    
    mongodb = get_mongodb()
    redis = await init_redis()
    qdrant_client = init_qdrant()
    
    return {
        "mongodb": mongodb,
        "redis": redis,
        "qdrant_client": qdrant_client
    }
