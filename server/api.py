from typing import Union
from fastapi import FastAPI
from backend.EmbeddingBot import EmbeddingBot

app = FastAPI()

# Initialize the EmbeddingBot instance
embedding_bot = EmbeddingBot(api_key="your_api_key_here")  # Replace with actual API key handling
@app.get("/")
def read_root():
    return {"message": "Welcome to the EmbeddingBot API"}

@app.get("/query")
def query_collection(query_text: str, n_results: int = 1) -> dict:
    # Placeholder implementation
    return {"query_text": query_text, "n_results": n_results, "results": []}