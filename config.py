import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Azure keys
ACCOUNT_URL = os.getenv("AZURE_ACCOUNT_URL")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")
BLOB_ACCESS_KEY = os.getenv("BLOB_ACCESS_KEY")
# Qdrant keys
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "https://21cdf154-5bc6-4325-bd5d-965464adfde7.us-west-2-0.aws.cloud.qdrant.io")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default paths
DIR = Path(__file__).resolve().parent.parent
DB_PATH = DIR / "testing" / "database"
SOURCE_DIR = DIR / "testing" / "Notes"