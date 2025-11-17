"""
Azure Blob Storage to Qdrant RAG Pipeline

This module implements a complete RAG pipeline:
1. Load documents from Azure Blob Storage (PDFs, DOCX, Markdown, CSVs, TXT)
2. Parse into LangChain Document objects with metadata
3. Chunk documents using text splitters
4. Generate embeddings using OpenAI
5. Store in Qdrant vector database
"""

import logging
from typing import List, Optional, Union
from pathlib import Path

from langchain_azure_storage.document_loaders import AzureBlobStorageLoader
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models

from config import (
    ACCOUNT_URL,
    BLOB_CONTAINER,
    BLOB_ACCESS_KEY,
    QDRANT_API_KEY,
    OPENAI_API_KEY,
    QDRANT_URL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Complete RAG pipeline for ingesting documents from Azure Blob Storage
    and storing them in Qdrant vector database.
    """

    # Embedding model dimensions
    EMBEDDING_DIM = 1536  # text-embedding-3-small dimension
    EMBEDDING_MODEL = "text-embedding-3-small"

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        chunk_size: int = 1500,
        chunk_overlap: int = 200,
        qdrant_url: Optional[str] = None,
    ):
        """
        Initialize the ingestion pipeline.

        Args:
            collection_name: Name of the Qdrant collection
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            qdrant_url: Qdrant server URL (defaults to config)
        """
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )

        # Initialize Qdrant client
        self.qdrant_url = qdrant_url or QDRANT_URL
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=QDRANT_API_KEY,
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        # Ensure collection exists with correct configuration
        self._ensure_collection()

    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        if not self.qdrant_client.collection_exists(self.collection_name):
            logger.info(f"Creating collection '{self.collection_name}'")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")
        else:
            logger.info(f"Collection '{self.collection_name}' already exists")

    def _get_loader_factory(self, file_extension: str):
        """
        Get appropriate loader factory based on file extension.

        Args:
            file_extension: File extension (e.g., '.pdf', '.docx')

        Returns:
            Loader class or None for text files
        """
        extension = file_extension.lower()
        loader_map = {
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            ".doc": Docx2txtLoader,
            ".md": UnstructuredMarkdownLoader,
            ".markdown": UnstructuredMarkdownLoader,
            ".csv": CSVLoader,
            ".txt": TextLoader,
        }
        return loader_map.get(extension, TextLoader)

    def load_documents_from_azure(
        self,
        blob_names: Optional[List[str]] = None,
        directory: str = "",
        file_extensions: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Load documents from Azure Blob Storage.

        Args:
            blob_names: Specific blob names to load (if None, loads all)
            directory: Directory path within container (optional)
            file_extensions: Filter by file extensions (e.g., ['.pdf', '.docx'])

        Returns:
            List of LangChain Document objects
        """
        logger.info(f"Loading documents from Azure Blob Storage: {BLOB_CONTAINER}")

        # Build blob paths
        if blob_names:
            blob_paths = [
                f"{directory}/{name}".strip("/") if directory else name
                for name in blob_names
            ]
        else:
            # Load all blobs from directory
            blob_paths = None

        # Create loader
        loader = AzureBlobStorageLoader(
            account_url=ACCOUNT_URL,
            container_name=BLOB_CONTAINER,
            blob_names=blob_paths,
            credential=BLOB_ACCESS_KEY,
        )

        # Load documents
        try:
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from Azure Blob Storage")

            # Filter by file extension if specified
            if file_extensions:
                filtered_docs = []
                for doc in documents:
                    # Extract file extension from metadata or source
                    source = doc.metadata.get("source", "")
                    if any(source.lower().endswith(ext.lower()) for ext in file_extensions):
                        filtered_docs.append(doc)
                documents = filtered_docs
                logger.info(f"Filtered to {len(documents)} documents matching extensions: {file_extensions}")

            return documents
        except Exception as e:
            logger.error(f"Error loading documents from Azure Blob Storage: {e}")
            raise

    def load_documents_with_parsing(
        self,
        blob_names: List[str],
        directory: str = "",
    ) -> List[Document]:
        """
        Load documents with appropriate parsing based on file type.

        Args:
            blob_names: List of blob names to load
            directory: Directory path within container

        Returns:
            List of parsed LangChain Document objects
        """
        all_documents = []

        for blob_name in blob_names:
            # Determine file extension
            file_path = Path(blob_name)
            extension = file_path.suffix

            # Get appropriate loader
            loader_class = self._get_loader_factory(extension)

            # Build full blob path
            blob_path = f"{directory}/{blob_name}".strip("/") if directory else blob_name

            logger.info(f"Loading {blob_path} with {loader_class.__name__}")

            try:
                # Create loader for this specific blob
                loader = AzureBlobStorageLoader(
                    account_url=ACCOUNT_URL,
                    container_name=BLOB_CONTAINER,
                    blob_names=[blob_path],
                    credential=BLOB_ACCESS_KEY,
                    loader_factory=lambda path: loader_class(path) if loader_class else None,
                )

                docs = loader.load()
                all_documents.extend(docs)
                logger.info(f"Successfully loaded {len(docs)} pages/chunks from {blob_name}")

            except Exception as e:
                logger.error(f"Error loading {blob_name}: {e}")
                continue

        return all_documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: List of LangChain Document objects

        Returns:
            List of chunked Document objects
        """
        logger.info(f"Chunking {len(documents)} documents")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def store_in_qdrant(self, documents: List[Document], batch_size: int = 100):
        """
        Store documents in Qdrant vector database.

        Args:
            documents: List of chunked Document objects
            batch_size: Number of documents to process in each batch
        """
        if not documents:
            logger.warning("No documents to store")
            return

        logger.info(f"Storing {len(documents)} documents in Qdrant collection '{self.collection_name}'")

        try:
            # Use LangChain's QdrantVectorStore for easy integration
            vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )

            # Add documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vector_store.add_documents(batch)
                logger.info(f"Stored batch {i // batch_size + 1} ({len(batch)} documents)")

            logger.info(f"Successfully stored all {len(documents)} documents in Qdrant")

        except Exception as e:
            logger.error(f"Error storing documents in Qdrant: {e}")
            raise

    def ingest(
        self,
        blob_names: Optional[List[str]] = None,
        directory: str = "",
        file_extensions: Optional[List[str]] = None,
        use_parsing: bool = True,
    ) -> dict:
        """
        Complete ingestion pipeline: Load → Chunk → Embed → Store.

        Args:
            blob_names: Specific blob names to load (if None, loads all)
            directory: Directory path within container
            file_extensions: Filter by file extensions
            use_parsing: Use file-specific parsers (PDF, DOCX, etc.)

        Returns:
            Dictionary with ingestion results and statistics
        """
        logger.info("Starting ingestion pipeline")

        try:
            # Step 1: Load documents
            if use_parsing and blob_names:
                documents = self.load_documents_with_parsing(blob_names, directory)
            else:
                documents = self.load_documents_from_azure(
                    blob_names=blob_names,
                    directory=directory,
                    file_extensions=file_extensions,
                )

            if not documents:
                logger.warning("No documents loaded")
                return {
                    "status": "warning",
                    "message": "No documents loaded",
                    "documents_loaded": 0,
                    "chunks_created": 0,
                    "documents_stored": 0,
                }

            # Step 2: Chunk documents
            chunks = self.chunk_documents(documents)

            # Step 3: Store in Qdrant (embedding happens automatically)
            self.store_in_qdrant(chunks)

            result = {
                "status": "success",
                "message": "Ingestion completed successfully",
                "documents_loaded": len(documents),
                "chunks_created": len(chunks),
                "documents_stored": len(chunks),
            }

            logger.info(f"Ingestion completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "documents_loaded": 0,
                "chunks_created": 0,
                "documents_stored": 0,
            }


# Convenience function for backward compatibility
def load_documents_from_azure(
    blob_names: List[str],
    directory: str = "",
    pdf: bool = False,
) -> List[Document]:
    """
    Legacy function for loading documents from Azure Blob Storage.

    Args:
        blob_names: List of blob names to load
        directory: Directory path within container
        pdf: Whether files are PDFs (deprecated, auto-detected now)

    Returns:
        List of LangChain Document objects
    """
    pipeline = IngestionPipeline()
    return pipeline.load_documents_with_parsing(blob_names, directory)
