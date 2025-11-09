import os
import json
import uuid
import re
from datetime import datetime
from typing import Dict, List
from tqdm import tqdm

# Azure SDK imports
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
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# Simple configuration variables at the top
conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
search_endpoint = os.environ.get("SEARCH_SERVICE_ENDPOINT")
search_key = os.environ.get("SEARCH_ADMIN_KEY")
project_endpoint = os.environ.get("PROJECT_ENDPOINT")
embeddings_model = os.environ.get("EMBEDDINGS_MODEL", "text-embedding-ada-002")
processed_container = "processed-documents"
search_index_name = "insurance-documents-index"
chunk_size = 1000
chunk_overlap = 200

# Step 2: Initialize Azure clients
print("🔄 Initializing Azure clients...")

blob_service_client = BlobServiceClient.from_connection_string(conn_str)
search_credential = AzureKeyCredential(search_key)
search_index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)
search_client = SearchClient(endpoint=search_endpoint, index_name=search_index_name, credential=search_credential)
project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
embeddings_client = project_client.inference.get_embeddings_client()

print("✅ Azure clients initialized")

# Step 3: Create Azure AI Search Index
print(f"🚀 Creating search index: {search_index_name}")

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

semantic_search = SemanticSearch(configurations=[semantic_config])

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
    name=search_index_name,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search
)

result = search_index_client.create_or_update_index(index)
print(f"✅ Search index '{search_index_name}' created successfully")

# Step 4: Text chunking functionality
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def chunk_text_for_search(text: str, metadata: Dict) -> List[Dict]:
    text = clean_text(text)
    chunks = []
    
    if len(text) <= chunk_size:
        return [{
            'content': text,
            'chunk_id': 0,
            'chunk_count': 1,
            'metadata': metadata.copy()
        }]
    
    start = 0
    chunk_id = 0
    
    while start < len(text):
        end = start + chunk_size
        
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
        
        start = max(start + chunk_size - chunk_overlap, end)
    
    for chunk in chunks:
        chunk['chunk_count'] = len(chunks)
    
    return chunks

# Step 5: Retrieve documents from blob storage
print(f"📥 Retrieving processed documents from blob storage...")

container_client = blob_service_client.get_container_client(processed_container)
blob_client = container_client.get_blob_client("processed_documents_for_vectorization.json")
blob_data = blob_client.download_blob().readall()
processed_documents = json.loads(blob_data.decode('utf-8'))

print(f"✅ Retrieved documents from blob storage")

# Process only policy documents
policies_only = {'policies': processed_documents.get('policies', [])}
search_documents = []

print(f"📂 Processing policy documents...")

for category, docs in policies_only.items():
    successful_docs = [doc for doc in docs if doc.get('success', False)]
    print(f"✅ Processing {len(successful_docs)} successful {category} documents")
    
    for doc in tqdm(successful_docs, desc=f"Processing {category}"):
        text_content = doc.get('text', '')
        if not text_content:
            continue
        
        metadata = doc.get('metadata', {}).copy()
        metadata['category'] = category
        
        chunks = chunk_text_for_search(text_content, metadata)
        
        for chunk in chunks:
            embedding_response = embeddings_client.embed(
                input=chunk['content'],
                model=embeddings_model
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

print(f"✅ Prepared {len(search_documents)} policy document chunks")

# Step 6: Upload documents to Azure AI Search
print(f"📤 Uploading documents to search index...")

batch_size = 50
total_docs = len(search_documents)

for i in tqdm(range(0, total_docs, batch_size), desc="Uploading batches"):
    batch = search_documents[i:i + batch_size]
    result = search_client.upload_documents(documents=batch)

print(f"✅ Upload completed!")
print(f"📊 Indexed {len(search_documents)} policy document chunks")
