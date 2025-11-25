from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from .Ingestion import IngestionPipeline
from config import (
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

    def __init__(self, openai_api_key: str, collection_name: str = QDRANT_COLLECTION_NAME,directory: str = "Finance",):
        
        self.collection_name = collection_name
        self.directory = directory
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
    
    # Class methods
    def InitiatePipeline(self, qdrant_url: str):
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
            qdrant_url=qdrant_url,
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
        
    def process_user_prompts(self, query:str, model:str="text-embedding-3-small") -> list[float]:
        query = query.replace("\n"," ")
        return self.openai_client.embeddings.create(model=model, input=query, dimensions=1536).data[0].embedding
    
    def retrieve_similar_documents(self, query_embedding:list[float], top_k:int=3) -> list[ScoredPoint]:
        """Retrieve similar documents from the Qdrant collection.

        Args:
            query_embedding (list[float]): The embedding vector for the query.
            top_k (int, optional): The number of top similar documents to retrieve. Defaults to 3.

        Raises:
            ValueError: If the query_embedding is not of length 1536.
            ValueError: If top_k is not positive.
            Exception: If there is an error retrieving documents from Qdrant.

        Returns:
            list[ScoredPoint]: A list of scored points representing the similar documents.
        """
        
        
        if len(query_embedding) != 1536:
            raise ValueError(f"Query embedding must be of length 1536, got {len(query_embedding)}.")
        if top_k <= 0:
            raise ValueError(f"top_k must be positive, got {top_k}.")
        elif top_k > 100:
            raise ValueError(f"top_k must not exceed 100, got {top_k}.")
        
        try:
            response = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )
            return response.points
            
        except Exception as e:
            raise Exception(f"Error retrieving similar documents: {e}") from e