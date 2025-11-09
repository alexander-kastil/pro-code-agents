from typing import Optional, Tuple

from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import EmbeddingsClient
from azure.identity import DefaultAzureCredential


def initialize_clients(
    storage_connection_string: str,
    search_endpoint: str,
    search_admin_key: str,
    search_index_name: str,
    inference_endpoint: str,
    inference_key: Optional[str],
    embeddings_model: str,
) -> Tuple[BlobServiceClient, SearchIndexClient, SearchClient, EmbeddingsClient]:
    blob_service_client = BlobServiceClient.from_connection_string(
        storage_connection_string
    )
    
    search_credential = AzureKeyCredential(search_admin_key)
    
    search_index_client = SearchIndexClient(
        endpoint=search_endpoint,
        credential=search_credential
    )
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index_name,
        credential=search_credential
    )
    
    if inference_key:
        embeddings_credential = AzureKeyCredential(inference_key)
        auth_note = "API key"
    else:
        embeddings_credential = DefaultAzureCredential()
        auth_note = "DefaultAzureCredential"
    
    embeddings_client = EmbeddingsClient(
        endpoint=inference_endpoint,
        credential=embeddings_credential,
        model=embeddings_model,
    )
    
    containers = list(blob_service_client.list_containers())
    print(f"✅ Connected to Blob Storage - Found {len(containers)} containers")
    
    print(f"✅ Connected to Azure AI Search - Service is available")
    print(f"✅ Connected to Azure AI Inference - Endpoint: {inference_endpoint} ({auth_note})")
    
    return blob_service_client, search_index_client, search_client, embeddings_client
