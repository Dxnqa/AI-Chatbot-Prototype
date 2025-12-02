from .server.Chat import Chat
from .database.Agent import RAG
from qdrant_client import QdrantClient, models
from config import QDRANT_URL,QDRANT_API_KEY, OPENAI_API_KEY, QDRANT_COLLECTION_NAME

# # System configurations
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# agent = RAG(collection_name=QDRANT_COLLECTION_NAME, directory="Finance", openai_api_key=OPENAI_API_KEY)
# agent.InitiatePipeline(qdrant_url=QDRANT_URL)

# client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)  # For testing purposes only
# print("Collection deleted for testing purposes.")

print(client.get_collection(collection_name=QDRANT_COLLECTION_NAME).points_count)  # Verify collection point count