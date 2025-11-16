import os
import sys
from typing import Union, List, Optional
from fastapi import FastAPI
from backend.EmbeddingBot import EmbeddingBot
from config import OPENAI_API_KEY, DB_PATH, SOURCE_DIR
from pydantic import BaseModel, Field

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY environment variable is not set.\nPlease set it and re-run the script.")
    sys.exit(1)

assistant = EmbeddingBot(api_key=OPENAI_API_KEY, db_path=DB_PATH)

collect_files = assistant.collect_files(source_dir=SOURCE_DIR)

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

# FastAPI application instance.
app = FastAPI()

sample_query = "Can I recover files in Linux?"

response = assistant.response(prompt=sample_query, n_results=1)

@app.get("/")
def read_root():
    return {"message": "Welcome to the EmbeddingBot API"}

@app.put("/prompt/{prompt_id}")
async def get_prompt_response(prompt_id: int, prompt: AIPrompt,q: str) -> dict[str, str]:
    result = {"prompt_id": prompt_id, **prompt.dump()}
    if q:
        result["response"] = response
    return result