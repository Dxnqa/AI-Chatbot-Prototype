import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Azure keys
ACCOUNT_URL = os.getenv("AZURE_ACCOUNT_URL")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")

# Qdrant keys
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default paths
DIR = Path(__file__).resolve().parent.parent
DB_PATH = DIR / "testing" / "database"
SOURCE_DIR = DIR / "testing" / "Notes"