"""
Qdrant Database Configuration

This module provides Qdrant client initialization and collection management.
The embedding dimension is set to 1536 for OpenAI's text-embedding-3-small model.
"""

from qdrant_client import QdrantClient, models
from config import QDRANT_API_KEY, QDRANT_URL

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Embedding dimension for OpenAI text-embedding-3-small
EMBEDDING_DIM = 1536

def ensure_collection(collection_name: str = "knowledge_base") -> None:
    """
    Ensure a Qdrant collection exists with the correct configuration.
    
    Args:
        collection_name: Name of the collection to create/verify
    """
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE
            )
        )
        print(f"Collection '{collection_name}' created with dimension {EMBEDDING_DIM}")
    else:
        print(f"Collection '{collection_name}' already exists")

# Initialize default collection
if __name__ == "__main__":
    ensure_collection("knowledge_base")
