from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# Environment variables
ACCOUNT_URL = os.getenv("AZURE_ACCOUNT_URL")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")

# Initialize Blob Service Client
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=ACCOUNT_URL, credential=credential)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

# Testing Lines
user_search = input("Search for document: ")

target = user_search

# Iterate through container to find target blob. Read if found, else raise error.
for blob in container_client.list_blobs():
    if blob.name == target:
        print(f"Found blob: {blob.name}")
        blob_client = container_client.get_blob_client(target)
        break
else:
    raise FileNotFoundError(f"{target} not found in the specified container.")

# Download and read blob content
data = blob_client.download_blob().readall().decode('utf-8')
print(data)