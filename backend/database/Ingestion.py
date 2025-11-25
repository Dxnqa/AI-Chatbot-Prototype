from typing import List, Optional
import logging
import uuid
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from langchain_azure_storage.document_loaders import AzureBlobStorageLoader
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct
from config import (
    ACCOUNT_URL,
    BLOB_CONTAINER,
    QDRANT_API_KEY,
    OPENAI_API_KEY,
    QDRANT_URL,
    QDRANT_COLLECTION_NAME
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


class IngestionPipeline:
    """
    A complete RAG ingestion pipeline that:
    1. Loads documents from Azure Blob Storage
    2. Parses them into LangChain Document objects
    3. Chunks the documents
    4. Generates embeddings
    5. Stores them in Qdrant vector database
    """
    
    def __init__(
        self,
        qdrant_url: str = QDRANT_URL,
        collection_name: str = QDRANT_COLLECTION_NAME,
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the ingestion pipeline.
        
        Args:
            qdrant_url: Qdrant instance URL
            collection_name: Name of the Qdrant collection
            embedding_model: OpenAI embedding model name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=QDRANT_API_KEY
        )
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=OPENAI_API_KEY
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        # Ensure collection exists with correct vector size
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create Qdrant collection if it doesn't exist with correct vector dimensions.
        
            Also creates payload indexes for match searching.
        """
        embedding_dim = 1536  # OpenAI text-embedding-3-small dimension
        
        if not self.qdrant_client.collection_exists(self.collection_name):
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_dim,
                    distance=models.Distance.COSINE
                )
            )
            logging.info(f"Created collection '{self.collection_name}' with vector size {embedding_dim}")
        else:
            # Verify collection has correct vector size
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            if collection_info.config.params.vectors.size != embedding_dim:
                logging.warning(
                    f"Collection '{self.collection_name}' has vector size "
                    f"{collection_info.config.params.vectors.size}, expected {embedding_dim}"
                )
                
        try:
            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="title",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            logging.info("Created payload index for 'title' field")
        except Exception as e:
            if "already exists" not in str(e).lower():
                logging.warning(f"Could not create title index: {e}")

                
    def update_collection(self, collection_name: str = QDRANT_COLLECTION_NAME):
        """Update the collection name if needed."""
        self.collection_name = collection_name
        self._ensure_collection_exists()
        
    
    def _get_loader_factory(self, file_type: str):
        """
        Get the appropriate LangChain loader factory based on file type.
        
        Args:
            file_type: File extension or type (pdf, txt, csv, md, etc.)
            
        Returns:
            Loader class or None
        """
        file_type = file_type.lower()
        loader_map = {
            "pdf": PyPDFLoader,
            "txt": TextLoader,
            "csv": CSVLoader,
            "md": UnstructuredMarkdownLoader,
            "markdown": UnstructuredMarkdownLoader,
        }
        return loader_map.get(file_type)
    
    def list_all_blob_names(self, directory: str = "Finance", file_extension: Optional[str] = None, credential: str = DefaultAzureCredential) -> list[str]:
        """List all blob names in the specified directory.

        Args:
            directory (str, optional): The directory to search for blobs. Defaults to "Finance".
            file_extension (Optional[str], optional): Filter blobs by file extension. Defaults to None.
            credential (str, optional): Azure credential for authentication. Defaults to DefaultAzureCredential.
        Returns:
            list[str]: list of blob names
        """
        blob_service_client = BlobServiceClient(account_url=ACCOUNT_URL, credential=credential)
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER)
        
        blob_names = []
        blob_names.extend(
            blob.name.replace(f"{directory}/", "").replace(f"{directory}\\", "")
            for blob in container_client.list_blobs(name_starts_with=directory)
            if file_extension is None or blob.name.endswith(file_extension)
        )
        logging.info(f"Found {len(blob_names)} blobs in directory '{directory}'")
        return blob_names

    
    def load_documents_from_azure(
        self,
        blob_names: List[str],
        directory: str = "",
        file_type: Optional[str] = None,
    ) -> List[Document]:
        """
        Load documents from Azure Blob Storage.
        
        Args:
            blob_names: List of blob names to load
            directory: Directory path in blob container (optional)
            file_type: File type/extension (pdf, txt, csv, md). If None, auto-detect from blob name.
            
        Returns:
            List of LangChain Document objects
        """
        # Build full blob paths
        blob_paths = []
        for blob_name in blob_names:
            if directory:
                full_path = blob_name if blob_name.startswith(directory) else f"{directory}/{blob_name}"
            else:
                full_path = blob_name
            blob_paths.append(full_path)
        
        # Auto-detect file type if not provided
        if file_type is None and blob_names:
            file_ext = blob_names[0].split(".")[-1].lower()
            file_type = file_ext
        
        # Get appropriate loader factory
        loader_factory = self._get_loader_factory(file_type) if file_type else None
        
        # Create loader
        loader = AzureBlobStorageLoader(
            account_url=ACCOUNT_URL,
            container_name=BLOB_CONTAINER,
            blob_names=blob_paths,
            loader_factory=loader_factory,
        )
        
        # Load documents
        documents = loader.load()
        logging.info(f"Loaded {len(documents)} documents from Azure Blob Storage")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        logging.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def embed_and_store(
        self,
        documents: List[Document],
        batch_size: int = 100,
    ) -> dict:
        """
        Generate embeddings and store documents in Qdrant.
        
        Args:
            documents: List of LangChain Document objects (chunked)
            batch_size: Number of documents to process in each batch
            
        Returns:
            Dictionary with ingestion statistics
        """
        total_docs = len(documents)
        stored_count = 0
        errors = []
        
        # Process in batches
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                points = self.process_batch(batch)
                self.upsert_to_qdrant(points)
                stored_count += len(points)
                logging.info(f"Stored batch {i//batch_size + 1}: {len(points)} documents")
            except Exception as e:
                error_msg = f"Error processing batch {i//batch_size + 1}: {str(e)}"
                logging.exception(error_msg)
                errors.append(error_msg)
        
        result = {
            "status": "partial" if errors else "success",
            "total_documents": total_docs,
            "stored_count": stored_count,
            "errors": errors,
        }
        
        logging.info(f"Ingestion complete: {stored_count}/{total_docs} documents stored")
        return result
        
    # Create points for Qdrant
    def create_points(self, texts, embeddings, metadatas):
        """
        Create points for Qdrant.
        
        Args:
            texts: List of texts to embed
            embeddings: List of embeddings
            metadatas: List of metadata
            
        Returns:
            List of PointStruct objects
        """
        points = []
        for text, embedding, metadata in zip(texts, embeddings, metadatas):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": text,
                        **metadata,
                    }
                )
            )
        return points
        
    # Extract texts and metadata
    def extract_from_documents(self, batch: List[Document]):
        texts = [doc.page_content for doc in batch]
        metadatas = []
        for doc in batch:
            metadata = doc.metadata.copy()
            # Extract title from source (blob path) if not already present
            if "title" not in metadata:
                source = metadata.get("source", "")
                # Extract filename from source path
                if source:
                    # Handle different source formats (Azure blob paths, local paths, etc.)
                    title = source.split("/")[-1]  # Get last part of path
                    # Remove query parameters if present
                    title = title.split("?")[0]
                    metadata["title"] = title
            metadatas.append(metadata)
        return texts, metadatas
    
    # Generate embeddings
    def embed_documents(self, texts: List[str]):
        return self.embeddings.embed_documents(texts)
    
    # Upsert to Qdrant
    def upsert_to_qdrant(self, points: List[PointStruct]):
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    # Process batch of documents before embedding and storing in Qdrant
    def process_batch(self, batch: List[Document]):
        texts, metadatas = self.extract_from_documents(batch)
        embeddings = self.embed_documents(texts)
        return self.create_points(texts, embeddings, metadatas)
    
    def ingest_from_azure(
        self,
        blob_names: List[str],
        directory: str = "",
        file_type: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> dict:
        """
        Complete ingestion pipeline: Load -> Chunk -> Embed -> Store.
        
        Args:
            blob_names: List of blob names to ingest
            directory: Directory path in blob container
            file_type: File type/extension (pdf, txt, csv, md)
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap
            
        Returns:
            Dictionary with ingestion results
        """
        # Override text splitter settings if provided
        if chunk_size or chunk_overlap:
            current_chunk_size = chunk_size if chunk_size else self.chunk_size
            current_chunk_overlap = chunk_overlap if chunk_overlap else self.chunk_overlap
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=current_chunk_size,
                chunk_overlap=current_chunk_overlap,
                length_function=len,
            )
        
        # Step 1: Load documents from Azure
        documents = self.load_documents_from_azure(
            blob_names=blob_names,
            directory=directory,
            file_type=file_type,
        )
        
        if not documents:
            return {
                "status": "error",
                "message": "No documents loaded from Azure Blob Storage",
            }
        
        # Step 2: Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Step 3: Embed and store in Qdrant
        return self.embed_and_store(chunks)