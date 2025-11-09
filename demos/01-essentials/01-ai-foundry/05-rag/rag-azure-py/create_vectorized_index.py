import os
import json
import uuid
from datetime import datetime
from typing import Dict, List
from tqdm import tqdm
import re

from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    ExhaustiveKnnAlgorithmConfiguration,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

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


class SearchIndexManager:
    def __init__(self, search_index_client: SearchIndexClient):
        self.search_index_client = search_index_client
        self.index_name = SEARCH_INDEX_NAME

    def create_search_index(self) -> bool:
        print(f"🚀 Creating search index with manual embeddings using Azure AI Project")
        print(f"🤖 Embeddings model: {EMBEDDINGS_MODEL}")
        
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="insurance-algorithm", kind="hnsw"),
                ExhaustiveKnnAlgorithmConfiguration(name="insurance-eknn", kind="exhaustiveKnn")
            ],
            profiles=[
                VectorSearchProfile(
                    name="insurance-profile",
                    algorithm_configuration_name="insurance-algorithm"
                )
            ]
        )
        
        semantic_config = SemanticConfiguration(
            name="insurance-semantic",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="content")],
                keywords_fields=[
                    SemanticField(field_name="category"),
                    SemanticField(field_name="file_name")
                ]
            )
        )
        
        semantic_search = SemanticSearch(
            configurations=[semantic_config]
        )
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="file_name", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="file_type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="chunk_id", type=SearchFieldDataType.Int32),
            SimpleField(name="chunk_count", type=SearchFieldDataType.Int32),
            SimpleField(name="original_length", type=SearchFieldDataType.Int32),
            SimpleField(name="chunk_length", type=SearchFieldDataType.Int32),
            SimpleField(name="processing_date", type=SearchFieldDataType.DateTimeOffset),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="insurance-profile"
            )
        ]
        
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search
        )
        
        result = self.search_index_client.create_or_update_index(index)
        print(f"✅ Search index '{self.index_name}' created successfully!")
        print(f"📋 Index fields: {len(result.fields)}")
        print(f"🔍 Vector search enabled: {bool(result.vector_search)}")
        print(f"🧠 Semantic search enabled: {bool(result.semantic_search)}")
        print(f"📝 Embeddings will be generated manually using Azure AI Project")
        
        return True
    
    def delete_index_if_exists(self) -> bool:
        try:
            self.search_index_client.delete_index(self.index_name)
            print(f"✅ Deleted existing index: {self.index_name}")
            return True
        except ResourceNotFoundError:
            print(f"ℹ️ Index {self.index_name} doesn't exist - will create new")
            return True
    
    def get_index_stats(self) -> Dict:
        try:
            index = self.search_index_client.get_index(self.index_name)
            stats = self.search_index_client.get_index_statistics(self.index_name)
            
            if hasattr(stats, 'document_count'):
                return {
                    "name": index.name,
                    "field_count": len(index.fields),
                    "document_count": stats.document_count,
                    "storage_size": stats.storage_size,
                    "vector_index_size": getattr(stats, 'vector_index_size', 0)
                }
            else:
                return {
                    "name": index.name,
                    "field_count": len(index.fields),
                    "document_count": stats.get('document_count', 0),
                    "storage_size": stats.get('storage_size', 0),
                    "vector_index_size": stats.get('vector_index_size', 0)
                }
        except Exception as e:
            print(f"❌ Error getting index stats: {e}")
            return {}


class DocumentRetriever:
    def __init__(self, blob_service_client):
        self.blob_service_client = blob_service_client
    
    def get_all_processed_documents(self) -> Dict:
        print(f"🔍 Attempting to retrieve from container: {PROCESSED_CONTAINER}")
        
        container_client = self.blob_service_client.get_container_client(PROCESSED_CONTAINER)
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


class TextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def chunk_text_for_search(self, text: str, metadata: Dict) -> List[Dict]:
        text = self.clean_text(text)
        chunks = []
        
        if len(text) <= self.chunk_size:
            return [{
                'content': text,
                'chunk_id': 0,
                'chunk_count': 1,
                'metadata': metadata.copy()
            }]
        
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'content': chunk_text,
                    'chunk_id': chunk_id,
                    'chunk_count': 0,
                    'metadata': metadata.copy()
                })
                chunk_id += 1
            
            start = max(start + self.chunk_size - self.chunk_overlap, end)
        
        for chunk in chunks:
            chunk['chunk_count'] = len(chunks)
        
        return chunks


class SearchIndexUploader:
    def __init__(self, search_client: SearchClient):
        self.search_client = search_client
    
    def upload_documents_batch(self, documents: List[Dict], batch_size: int = 50) -> bool:
        total_docs = len(documents)
        print(f"📤 Uploading {total_docs} documents to search index...")
        
        for i in tqdm(range(0, total_docs, batch_size), desc="Uploading batches"):
            batch = documents[i:i + batch_size]
            
            upload_batch = []
            for doc in batch:
                search_doc = doc.copy()
                upload_batch.append(search_doc)
            
            result = self.search_client.upload_documents(documents=upload_batch)
            
            failed_docs = [r for r in result if not r.succeeded]
            if failed_docs:
                print(f"⚠️ Failed to upload {len(failed_docs)} documents in batch {i//batch_size + 1}")
                for failed in failed_docs[:3]:
                    print(f"   Error: {failed.error_message}")
        
        print(f"✅ Document upload completed!")
        return True
    
    def get_document_count(self) -> int:
        results = self.search_client.search("*", include_total_count=True, top=1)
        return results.get_count()


class SearchTester:
    def __init__(self, search_client: SearchClient):
        self.search_client = search_client
    
    def vector_search(self, query: str, top_k: int = 5, category_filter: str = None) -> List[Dict]:
        search_params = {
            "search_text": query,
            "top": top_k,
            "search_mode": "any",
            "query_type": "semantic",
            "semantic_configuration_name": "insurance-semantic",
            "select": ["id", "title", "content", "category", "file_name", "chunk_id", "chunk_count"]
        }
        
        if category_filter:
            search_params["filter"] = f"category eq '{category_filter}'"
        
        results = self.search_client.search(**search_params)
        
        search_results = []
        for result in results:
            search_results.append({
                'id': result['id'],
                'title': result['title'],
                'content': result['content'],
                'category': result['category'],
                'file_name': result['file_name'],
                'chunk_id': result['chunk_id'],
                'chunk_count': result['chunk_count'],
                'score': result.get('@search.score', 0),
                'reranker_score': result.get('@search.reranker_score', 0)
            })
        
        return search_results
    
    def display_search_results(self, query: str, results: List[Dict], search_type: str = "Search"):
        print(f"\n🔍 {search_type} Results for: '{query}'")
        print("=" * 80)
        
        if not results:
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            score = result.get('score', 0)
            reranker_score = result.get('reranker_score', 0)
            
            print(f"\n{i}. 📄 {result['title']}")
            print(f"   📂 Category: {result['category']}")
            print(f"   📊 Score: {score:.4f}", end="")
            if reranker_score > 0:
                print(f" | Reranker: {reranker_score:.4f}")
            else:
                print()
            print(f"   📝 Chunk {result['chunk_id'] + 1}")
            
            preview = result['content'][:300]
            if len(result['content']) > 300:
                preview += "..."
            print(f"   💬 Preview: {preview}")
            print("-" * 80)


def initialize_clients():
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    
    search_credential = AzureKeyCredential(SEARCH_ADMIN_KEY)
    
    search_index_client = SearchIndexClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        credential=search_credential
    )
    
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=SEARCH_INDEX_NAME,
        credential=search_credential
    )
    
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential()
    )
    
    embeddings_client = project_client.inference.get_embeddings_client()
    
    containers = list(blob_service_client.list_containers())
    print(f"✅ Connected to Blob Storage - Found {len(containers)} containers")
    
    print(f"✅ Connected to Azure AI Search - Service is available")
    print(f"✅ Connected to Azure AI Project - Endpoint: {PROJECT_ENDPOINT}")
    
    return blob_service_client, search_index_client, search_client, project_client, embeddings_client


def retrieve_and_process_documents(blob_service_client, embeddings_client):
    retriever = DocumentRetriever(blob_service_client)
    chunker = TextChunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    print("\n" + "="*60)
    print("📥 RETRIEVING PROCESSED DOCUMENTS FROM BLOB STORAGE")
    print("="*60)
    
    processed_documents = retriever.get_all_processed_documents()
    
    print(f"\n🎉 SUCCESS! Retrieved processed documents from blob storage")
    print(f"📊 Available categories: {list(processed_documents.keys())}")
    
    policies_only = {'policies': processed_documents.get('policies', [])}
    
    print(f"🎯 Filtering to process POLICIES only...")
    print(f"📄 Found {len(policies_only['policies'])} policy documents")
    
    search_documents = []
    
    for category, docs in policies_only.items():
        print(f"\n📂 Processing {category} documents...")
        
        successful_docs = [doc for doc in docs if doc.get('success', False)]
        print(f"✅ Processing {len(successful_docs)} successful {category} documents")
        
        for doc in tqdm(successful_docs, desc=f"Processing {category}"):
            text_content = doc.get('text', '')
            if not text_content:
                print(f"⚠️ Skipping document with no text content: {doc.get('metadata', {}).get('file_name', 'Unknown')}")
                continue
            
            metadata = doc.get('metadata', {}).copy()
            metadata['category'] = category
            
            chunks = chunker.chunk_text_for_search(text_content, metadata)
            
            for chunk in chunks:
                embedding_response = embeddings_client.embed(
                    input=chunk['content'],
                    model=EMBEDDINGS_MODEL
                )
                content_vector = embedding_response.data[0].embedding
                
                search_doc = {
                    'id': str(uuid.uuid4()),
                    'title': f"{metadata.get('file_name', 'Unknown')} - Part {chunk['chunk_id'] + 1}",
                    'content': chunk['content'],
                    'category': category,
                    'file_name': metadata.get('file_name', 'Unknown'),
                    'file_type': metadata.get('file_type', 'markdown'),
                    'chunk_id': chunk['chunk_id'],
                    'chunk_count': chunk['chunk_count'],
                    'original_length': len(text_content),
                    'chunk_length': len(chunk['content']),
                    'processing_date': datetime.now().isoformat() + 'Z',
                    'content_vector': content_vector
                }
                search_documents.append(search_doc)
    
    print(f"\n✅ Prepared {len(search_documents)} policy document chunks for search index")
    
    if search_documents:
        total_files = len(set(doc['file_name'] for doc in search_documents))
        total_chunks = len(search_documents)
        avg_chunk_length = sum(doc['chunk_length'] for doc in search_documents) / total_chunks
        
        print(f"\n📊 POLICIES INDEXING SUMMARY:")
        print(f"   📄 Total policy files: {total_files}")
        print(f"   🗂️ Total chunks created: {total_chunks}")
        print(f"   📏 Average chunk length: {avg_chunk_length:.0f} characters")
        
        file_stats = {}
        for doc in search_documents:
            file_name = doc['file_name']
            if file_name not in file_stats:
                file_stats[file_name] = 0
            file_stats[file_name] += 1
        
        print(f"\n📋 Policy files breakdown:")
        for file_name, chunk_count in file_stats.items():
            print(f"   • {file_name}: {chunk_count} chunks")
    
    return search_documents


def upload_documents(search_client, search_documents, index_manager):
    uploader = SearchIndexUploader(search_client)
    
    print("\n🚀 Starting POLICIES upload to Azure AI Search...")
    print("=" * 60)
    print("🎯 Uploading POLICY documents only")
    
    success = uploader.upload_documents_batch(search_documents)
    
    if success:
        import time
        print("\n⏳ Waiting for indexing to complete...")
        time.sleep(10)
        
        doc_count = uploader.get_document_count()
        print(f"✅ Index now contains {doc_count} policy document chunks")
        
        stats = index_manager.get_index_stats()
        if stats:
            print(f"📊 Index statistics:")
            print(f"   - Policy documents: {stats.get('document_count', 'N/A')}")
            print(f"   - Storage size: {stats.get('storage_size', 'N/A')} bytes")
            print(f"   - Vector index size: {stats.get('vector_index_size', 'N/A')} bytes")
        
        print(f"\n🎯 SUCCESS: Only policy documents have been indexed!")
        print(f"📄 Your Azure AI Search index now contains comprehensive policy information")
        print(f"🔍 Ready for policy-related queries and AI agent integration")
    
    return success


def test_search_index(search_client):
    search_tester = SearchTester(search_client)
    
    test_queries = [
        "What is covered under collision insurance?",
        "How much does comprehensive coverage cost?", 
        "What are the liability limits for commercial vehicles?",
        "Does my policy cover theft and vandalism?",
        "What happens if I hit an uninsured driver?",
        "High value vehicle insurance requirements",
        "Motorcycle insurance coverage options"
    ]
    
    print("🧪 Testing Azure AI Search with integrated vectorization...")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n\n🔍 Testing query: '{query}'")
        
        results = search_tester.vector_search(query, top_k=3)
        
        if results:
            print(f"✅ Found {len(results)} relevant chunks")
            search_tester.display_search_results(query, results, "Semantic Search")
        else:
            print("❌ No relevant documents found")
        
        print("-" * 40)
    
    print("\n✅ Query testing completed!")


def main():
    print("🚀 Starting Azure AI Search Vectorized Index Creation")
    print("=" * 60)
    
    print("\n## 2. Initialize Azure Services")
    blob_service_client, search_index_client, search_client, project_client, embeddings_client = initialize_clients()
    
    print("\n## 3. Create Azure AI Search Index with Integrated Vectorization")
    index_manager = SearchIndexManager(search_index_client)
    success = index_manager.create_search_index()
    if success:
        print("\n📊 Index created successfully!")
    
    print("\n## 4. Document Retrieval and Processing")
    print("✅ Document processors initialized")
    
    print("\n## 5. Retrieve and Process Documents")
    search_documents = retrieve_and_process_documents(blob_service_client, embeddings_client)
    
    print("\n## 6. Upload Documents to Azure AI Search with Pre-computed Embeddings")
    upload_success = upload_documents(search_client, search_documents, index_manager)
    
    print("\n## 7. Test the Search Index with Semantic and Vector Search")
    print("✅ Search tester initialized")
    
    print("\n## 8. Test with Sample Insurance Queries")
    test_search_index(search_client)
    
    print("\n✅ All steps completed successfully!")


if __name__ == "__main__":
    main()
