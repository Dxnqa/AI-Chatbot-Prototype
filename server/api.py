import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from typing import Union
from fastapi import FastAPI
from backend.EmbeddingBot import EmbeddingBot
from pathlib import Path

# System configurations. Set paths, load environment variables, and initialize EmbeddingBot.
DIR = Path(__file__).resolve().parent.parent
DB_PATH = DIR / "testing" / "database"
SOURCE_DIR = DIR / "testing" / "Notes"

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable is not set.\nPlease set it and re-run the script.")
    sys.exit(1)

assistant = EmbeddingBot(api_key=api_key, db_path=DB_PATH)

collect_files = assistant.collect_files(source_dir=SOURCE_DIR)

# FastAPI application instance.
app = FastAPI()

sample_query = "Can I recover files in Linux?"

query = assistant.query_collection(query_text=sample_query, n_results=1).get("documents", [])[0]

context = [f"{i}. {doc}" for i, doc in enumerate(query, start=1)]

response = assistant.llm_response(prompt=sample_query, context=context)

@app.get("/")
def read_root():
    return {"message": "Welcome to the EmbeddingBot API"}

@app.get("/prompt")
async def get_prompt_response() -> dict[str, str]:
    return {"response": response}