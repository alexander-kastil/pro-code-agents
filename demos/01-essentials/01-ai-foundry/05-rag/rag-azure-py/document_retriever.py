from azure.storage.blob import BlobServiceClient
import json
from typing import Dict


class DocumentRetriever:
    def __init__(self, blob_service_client: BlobServiceClient, container_name: str):
        self.blob_service_client = blob_service_client
        self.container_name = container_name
    
    def get_all_processed_documents(self) -> Dict:
        print(f"🔍 Attempting to retrieve from container: {self.container_name}")
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blob_name = "processed_documents_for_vectorization.json"
        print(f"📥 Downloading file: {blob_name}")
        
        blob_client = container_client.get_blob_client(blob_name)
        
        blob_props = blob_client.get_blob_properties()
        file_size = blob_props.size
        print(f"✅ File found - Size: {file_size / (1024*1024):.2f} MB")
        
        print("📥 Downloading blob content...")
        blob_data = blob_client.download_blob().readall()
        
        print("🔄 Parsing JSON content...")
        documents = json.loads(blob_data.decode('utf-8'))
        
        print(f"✅ Successfully downloaded and parsed processed documents")
        print(f"📊 Found categories: {list(documents.keys())}")
        
        for category, docs in documents.items():
            successful_docs = [d for d in docs if d.get('success', False)]
            print(f"   - {category}: {len(successful_docs)}/{len(docs)} successful documents")
        
        return documents
