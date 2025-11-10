from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNT_URL = os.getenv("AZURE_ACCOUNT_URL")
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=ACCOUNT_URL, credential=credential)

container_client = blob_service_client.get_container_client("documentation")

for blob in container_client.list_blobs():
    print(blob.name)