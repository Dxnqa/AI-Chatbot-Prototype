from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


qdrant_client = QdrantClient(
    url="https://21cdf154-5bc6-4325-bd5d-965464adfde7.us-west-2-0.aws.cloud.qdrant.io",
    api_key=QDRANT_API_KEY
)