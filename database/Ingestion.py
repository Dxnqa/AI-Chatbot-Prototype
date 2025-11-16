from langchain_azure_storage.document_loaders import AzureBlobStorageLoader
from langchain_community.document_loaders import PyPDFLoader
from config import BLOB_ACCESS_KEY, ACCOUNT_URL, BLOB_CONTAINER

# Loader = Azure Blob Storage Loader
# Using PyPDFLoader to load PDF files from Azure Blob Storage
# User query should specify the directory and blob names to load specific files
# PyPDF Loader is used to read PDF contents from the blobs

def load_documents_from_azure(blob_names: list[str], directory:str=""):
    loader = AzureBlobStorageLoader(
        account_url=ACCOUNT_URL,
        container_name=BLOB_CONTAINER,
        blob_names=[f"{directory}/{blob_name}" for blob_name in blob_names],
        loader_factory=PyPDFLoader
    )
    return loader

# Example usage:
prompt_directory = input("Enter the directory in the blob container (leave blank for root): ").strip()
blob_names_input = input("Enter the blob names (comma-separated): ")

print(f"Loading documents from blobs: {blob_names_input} in directory: {prompt_directory}")

docs = load_documents_from_azure(blob_names=blob_names_input.split(","), directory=prompt_directory).load()

for doc in docs:
    print(doc.page_content[:500])  # Print first 500 characters of each document