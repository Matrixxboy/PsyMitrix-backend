# rag/qdrant.py
# Service for interacting with the Qdrant vector database.

from qdrant_client import QdrantClient, models
from core.config import settings
from core.db import get_qdrant_client

# Point-wise comment: Function to get or create a Qdrant collection
def get_or_create_collection(client: QdrantClient, collection_name: str):
    try:
        client.get_collection(collection_name=collection_name)
    except Exception:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )

# Point-wise comment: Function to upsert a vector into Qdrant
async def upsert_vector(user_id: str, vector: list[float], payload: dict):
    client = get_qdrant_client()
    get_or_create_collection(client, settings.QDRANT_COLLECTION_NAME)
    
    client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=user_id,  # Using user_id as the point id
                vector=vector,
                payload=payload
            )
        ],
        wait=True
    )

# Point-wise comment: Function to search for similar vectors in Qdrant
async def search_vectors(query_vector: list[float], top_k: int = 5):
    client = get_qdrant_client()
    search_result = client.search(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return search_result
