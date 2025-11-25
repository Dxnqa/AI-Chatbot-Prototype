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
    def InitiatePipeline(self):
        """Initialize the ingestion pipeline.
        
        If the collection doesn't exist, it will:
        1. Create the collection
        2. Chunk documents
        3. Embed and store documents
        
        If the collection exists, the process is skipped to avoid duplication.
        """
        # Check if collection exists - if it does, skip to avoid duplication
        if self.qdrant_client.collection_exists(collection_name=self.collection_name):
            return
        
        # Collection doesn't exist - run the full pipeline
        pipeline = IngestionPipeline(
            collection_name=self.collection_name,
            embedding_model="text-embedding-3-small",
            chunk_size=1000,
            chunk_overlap=200
        )

        blob_names = pipeline.list_all_blobs_names(directory=self.directory)
        documents = pipeline.load_documents_from_azure(
            blob_names=blob_names,
            directory=self.directory
        )
        
        chunks = pipeline.chunk_documents(documents)
        
        pipeline.embed_and_store(chunks)