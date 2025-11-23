from qdrant_client import QdrantClient, models
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME
from .Ingestion import IngestionPipeline

# Qdrant client instance
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Collection configuration
EMBEDDING_DIM = 1536  # OpenAI text-embedding-3-small dimension

pipeline = IngestionPipeline(
    collection_name=QDRANT_COLLECTION_NAME,
    embedding_model="text-embedding-3-small",
    chunk_size=1000,
    chunk_overlap=200
)

# Verify if the collection exists, if not = create it.
ensure_collection_exists = pipeline._ensure_collection_exists
    
# Initialize collection on import
print(f"Collection count: {qdrant_client.get_collection(QDRANT_COLLECTION_NAME).points_count}")