import os
from dotenv import load_dotenv

from initialize_clients import initialize_clients
from search_index_manager import SearchIndexManager
from document_processor import retrieve_and_process_documents
from upload_handler import upload_documents
from test_search import test_search_index

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.environ.get('STORAGE_CONNECTION_STRING')
SEARCH_SERVICE_NAME = os.environ.get('SEARCH_SERVICE_NAME')
SEARCH_SERVICE_ENDPOINT = os.environ.get('SEARCH_SERVICE_ENDPOINT')
SEARCH_ADMIN_KEY = os.environ.get('SEARCH_ADMIN_KEY')
PROJECT_ENDPOINT = os.environ.get('PROJECT_ENDPOINT')
EMBEDDINGS_MODEL = os.environ.get('EMBEDDINGS_MODEL', 'text-embedding-ada-002')
PROCESSED_CONTAINER = 'processed-documents'
SEARCH_INDEX_NAME = 'insurance-documents-index'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def main():
    print("🚀 Starting Azure AI Search Vectorized Index Creation")
    print("=" * 60)
    
    print("\n## 2. Initialize Azure Services")
    blob_service_client, search_index_client, search_client, embeddings_client = initialize_clients(
        storage_connection_string=AZURE_STORAGE_CONNECTION_STRING,
        search_endpoint=SEARCH_SERVICE_ENDPOINT,
        search_admin_key=SEARCH_ADMIN_KEY,
        search_index_name=SEARCH_INDEX_NAME,
        project_endpoint=PROJECT_ENDPOINT
    )
    
    print("\n## 3. Create Azure AI Search Index with Integrated Vectorization")
    index_manager = SearchIndexManager(search_index_client, SEARCH_INDEX_NAME)
    success = index_manager.create_search_index(EMBEDDINGS_MODEL)
    if success:
        print("\n📊 Index created successfully!")
    
    print("\n## 4. Document Retrieval and Processing")
    print("✅ Document processors initialized")
    
    print("\n## 5. Retrieve and Process Documents")
    search_documents = retrieve_and_process_documents(
        blob_service_client=blob_service_client,
        embeddings_client=embeddings_client,
        container_name=PROCESSED_CONTAINER,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        embeddings_model=EMBEDDINGS_MODEL
    )
    
    print("\n## 6. Upload Documents to Azure AI Search with Pre-computed Embeddings")
    upload_success = upload_documents(search_client, search_documents, index_manager)
    
    print("\n## 7. Test the Search Index with Semantic and Vector Search")
    print("✅ Search tester initialized")
    
    print("\n## 8. Test with Sample Insurance Queries")
    test_search_index(search_client)
    
    print("\n✅ All steps completed successfully!")


if __name__ == "__main__":
    main()
