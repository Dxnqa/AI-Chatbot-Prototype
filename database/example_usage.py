"""
Example usage of the IngestionPipeline for RAG data ingestion.

This demonstrates how to ingest documents from Azure Blob Storage
into Qdrant vector database.
"""

from langchain_core.documents.base import Document
from .Ingestion import IngestionPipeline

# Initialize the ingestion pipeline
pipeline = IngestionPipeline(
    collection_name="knowledge_base",
    embedding_model="text-embedding-3-small",
    chunk_size=1000,
    chunk_overlap=200,
)

# # Example 1: Ingest PDF files from a specific directory
# result = pipeline.ingest_from_azure(
#     blob_names=["candlesticks.pdf", "Penny stock.pdf"],
#     directory="Finance",
#     file_type="pdf",
# )

# print(f"Ingestion result: {result}")

# # Example 2: Ingest text files with custom chunking
# result = pipeline.ingest_from_azure(
#     blob_names=["notes.txt", "summary.txt"],
#     directory="notes",
#     file_type="txt",
#     chunk_size=1500,
#     chunk_overlap=300,
# )

# print(f"Ingestion result: {result}")

# # Example 3: Ingest markdown files (auto-detect file type)
# result = pipeline.ingest_from_azure(
#     blob_names=["README.md", "guide.md"],
#     directory="docs",
#     # file_type will be auto-detected from .md extension
# )

# print(f"Ingestion result: {result}")

# # Example 4: Step-by-step pipeline (for more control)
# # Step 1: Load documents
documents = pipeline.load_documents_from_azure(
    blob_names=["candlesticks.pdf", "Penny stock.pdf"],
    directory="Finance",
    file_type="pdf",
)

# # Step 2: Chunk documents
# chunks = pipeline.chunk_documents(documents)

# # Step 3: Embed and store
# result = pipeline.embed_and_store(chunks, batch_size=50)

# print(f"Stored {result['stored_count']} chunks out of {result['total_documents']}")

print(f"Loaded {len(documents)} documents\n")

for i, doc in enumerate[Document](documents, 1):
    print(f"Document {i}")
    print(f"Source blob: {doc.metadata.get('source')}")
    print(f"Metadata: {doc.metadata}")     # full blob metadata
    print(f"Preview:\n{doc.page_content}")  # first 500 chars
    print("-" * 80)