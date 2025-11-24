from openai import OpenAI
from qdrant_client import QdrantClient, models
from .Ingestion import IngestionPipeline
from config import (
    OPENAI_API_KEY,
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME
    )


# Ingestion pipeline
class RAG:
    """A class for implementing Retrieval-Augmented Generation (RAG) using Qdrant and OpenAI.
    
    Args:
        collection_name (str): The name of the Qdrant collection to use. Default is taken from config.
        directory (str): The directory from which to load documents. Default is "Finance" for testing purposes.
    """

    def __init__(self, collection_name: str = QDRANT_COLLECTION_NAME, directory: str = "Finance"):
        self.collection_name = collection_name
        self.directory = directory
        
    # Client instances
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    # Class methods
    
    def InitiatePipeline(self, collection_exists: bool = False):
        """Initialize the ingestion pipeline.

        Args:
            collection_exists (bool, required): Whether the collection already exists. If False, the collection will be created. Otherwise, the existing collection will be used.
            directory (str, optional): The directory from which to load documents. Defaults to "Finance" for testing purposes.
        """
        if collection_exists:
            blob_names = self.list_all_blob_names(directory=self.directory)
            
            pipeline = IngestionPipeline(
                collection_name=self.collection_name,
                embedding_model="text-embedding-3-small",
                chunk_size=1000,
                chunk_overlap=200
            )  
            
            documents = pipeline.load_documents_from_azure(
                blob_names=blob_names,
                directory=self.directory,
            )