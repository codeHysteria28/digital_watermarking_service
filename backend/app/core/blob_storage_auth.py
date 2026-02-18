import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_BLOB_URL")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

if not STORAGE_ACCOUNT_URL:
    raise ValueError("Storage account url variable not found")

if not CONTAINER_NAME:
    raise ValueError("Container name variable not found")

blob_service_client = BlobServiceClient(STORAGE_ACCOUNT_URL, credential=DefaultAzureCredential())

def get_or_create_container(container_name: str = CONTAINER_NAME):
    container_client = blob_service_client.get_container_client(container_name)

    if not container_client.exists():
        container_client.create_container()
    
    return container_client