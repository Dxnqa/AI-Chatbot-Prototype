from typing import Union, List, Optional
import logging
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.server.Chat import Chat
from backend.database.Agent import RAG
from config import OPENAI_API_KEY, QDRANT_COLLECTION_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

class AIPrompt(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier for the prompt")
    title: str = Field(..., description="Short, human-readable name for the prompt")
    text: str = Field(..., description="The main prompt text to send to the AI model")
    temperature: float = Field(1.0, ge=0.0, le=2.0, description="Controls randomness")
    max_tokens: int = Field(512, gt=0, description="Maximum tokens in the response")
    tags: Optional[List[str]] = Field(default_factory=list, description="List of categories or tags")
    created_at: Optional[str] = Field(None, description="ISO timestamp of creation")
    updated_at: Optional[str] = Field(None, description="ISO timestamp of last update")
    author: Optional[str] = Field(None, description="User or system that created this prompt")
    
    
class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's input message for the AI model")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking chat history")
    user_id: Optional[str] = Field(None, description="Optional user identifier for tracking sessions")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation ID for tracking chat history")
    error: Optional[str] = Field(None, description="Error message if request failed")


# In-memory conversation store (placeholder for future memory implementation)
conversations: dict[str, list[dict]] = {}

# FastAPI application instance.
app = FastAPI(
    title="AI Chatbot API",
    description="API for the AI Chatbot with RAG capabilities",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG agent and Chat instance at startup
agent = RAG(collection_name=QDRANT_COLLECTION_NAME, directory="Finance", openai_api_key=OPENAI_API_KEY)
chat_instance = Chat(model="gpt-5.1", key=OPENAI_API_KEY, rag_agent=agent)
logger.info("Chat instance and RAG agent initialized successfully.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the EmbeddingBot API"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return an AI-generated response."""
    # Generate or use existing conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        logger.info(f"Processing chat request for conversation: {conversation_id}")
        
        # Initialize conversation history if new
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Store user message in conversation history
        conversations[conversation_id].append({
            "role": "user",
            "content": request.message
        })
        
        # Generate response using the Chat pipeline
        response_text = chat_instance.query_pipeline(request.message.strip())
        
        # Store assistant response in conversation history
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        logger.info(f"Successfully generated response for conversation: {conversation_id}")
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id
        )
        
    except ValueError as e:
        logger.error(f"Validation error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request parameters")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")