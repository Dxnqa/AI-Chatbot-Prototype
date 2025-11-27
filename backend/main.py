from .server.Chat import Chat
from .database.Agent import RAG
from qdrant_client import QdrantClient, models
from config import QDRANT_URL,QDRANT_API_KEY, OPENAI_API_KEY, QDRANT_COLLECTION_NAME

# # System configurations
# client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
agent = RAG(collection_name=QDRANT_COLLECTION_NAME, directory="Finance", openai_api_key=OPENAI_API_KEY)
# pipeline = agent.InitiatePipeline(qdrant_url=QDRANT_URL,)

# # Chatbot instance
chatbot = Chat(model="gpt-5-mini", key=OPENAI_API_KEY, rag_agent=agent)

user_input = input("Enter your question: ").strip()

print(f"\n{chatbot.query_pipeline(user_input)}")
