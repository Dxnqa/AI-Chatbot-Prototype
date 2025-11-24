from .server.Chat import Chat
from qdrant_client import QdrantClient, models
from config import QDRANT_URL,QDRANT_API_KEY, OPENAI_API_KEY
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

