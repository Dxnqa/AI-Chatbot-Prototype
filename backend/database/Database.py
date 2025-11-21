from qdrant_client import QdrantClient, models
from config import QDRANT_URL, QDRANT_API_KEY

# Qdrant client instance
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Collection configuration
COLLECTION_NAME = "knowledge_base"
EMBEDDING_DIM = 1536  # OpenAI text-embedding-3-small dimension

# Verify if the collection exists, if not = create it.
def ensure_collection_exists():
    """Ensure the Qdrant collection exists with correct vector dimensions."""
    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE
            )
        )
        print(f"Created collection '{COLLECTION_NAME}' with vector size {EMBEDDING_DIM}")
    else:
        # Verify collection has correct vector size
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        current_size = collection_info.config.params.vectors.size
        if current_size != EMBEDDING_DIM:
            print(
                f"Warning: Collection '{COLLECTION_NAME}' has vector size {current_size}, "
                f"expected {EMBEDDING_DIM}. Consider recreating the collection."
            )

# Initialize collection on import
ensure_collection_exists()
