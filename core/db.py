# core/db.py
# Database connection logic.
# This file handles connections to MongoDB and Qdrant.

from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient
from core.config import settings

# Point-wise comment: MongoDB connection
# A client for the MongoDB database is created here.
mongo_client: AsyncIOMotorClient = None

async def connect_to_mongo():
    """Connects to the MongoDB database."""
    global mongo_client
    mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Closes the MongoDB connection."""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("Closed MongoDB connection")

def get_mongo_db():
    """Returns the MongoDB database instance."""
    if mongo_client:
        print("MongoDB client is available")
        return mongo_client.get_default_database()
    return None

# Point-wise comment: Qdrant connection
# A client for the Qdrant vector database is created here.
qdrant_client: QdrantClient = None

async def connect_to_qdrant():
    """Connects to the Qdrant database."""
    global qdrant_client
    qdrant_client = QdrantClient(
        url=f"{settings.QDRANT_HOST}:{settings.QDRANT_PORT}",
        api_key=settings.QDRANT_API_KEY
    )
    print("Connected to Qdrant")

def get_qdrant_client():
    """Returns the Qdrant client instance."""
    if qdrant_client:
        print("Qdrant client is available")
    return qdrant_client