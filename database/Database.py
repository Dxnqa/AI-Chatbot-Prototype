from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv
load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


qdrant_client = QdrantClient(
    url="https://21cdf154-5bc6-4325-bd5d-965464adfde7.us-west-2-0.aws.cloud.qdrant.io",
    api_key=QDRANT_API_KEY
)
# Verify if the collection exists, if not = create it.
verify_collection = qdrant_client.collection_exists("knowledge_base")
if not verify_collection:
    qdrant_client.create_collection(
    collection_name="knowledge_base",
    vectors_config=models.VectorParams(
        size=100,
        distance=models.Distance.COSINE
    )
)
