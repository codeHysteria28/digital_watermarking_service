import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
load_dotenv()

credential = DefaultAzureCredential()
VAULT_URL = os.getenv("VAULT_URL")

if not VAULT_URL:
    raise ValueError("AZURE_KEYVAULT_URL env variable not found")

secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)

def get_secret(secret_name: str):
    secret = secret_client.get_secret(secret_name)

    return secret