from .server.Chat import Chat
from .database.Agent import Agent
from qdrant_client import QdrantClient, models
from config import QDRANT_URL,QDRANT_API_KEY, OPENAI_API_KEY

# System configurations
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
agent = Agent(collection_name="knowledge_base", directory="Finance", openai_api_key=OPENAI_API_KEY)
pipeline = agent.InitiatePipeline(qdrant_url=QDRANT_URL,)

