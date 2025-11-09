import os
import uuid
import re
from datetime import datetime
from typing import Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
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
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

load_dotenv()

conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
search_endpoint = os.environ.get("SEARCH_SERVICE_ENDPOINT")
search_key = os.environ.get("SEARCH_ADMIN_KEY")
project_endpoint = os.environ.get("PROJECT_ENDPOINT")
embeddings_model = os.environ.get("EMBEDDINGS_MODEL")
index_name = os.environ.get("AISEARCH_INDEX_NAME")
storage_container = os.environ.get("STORAGE_CONTAINER_NAME")
chunk_size = 1000
chunk_overlap = 200

blob_service_client = BlobServiceClient.from_connection_string(conn_str)
search_credential = AzureKeyCredential(search_key)
search_index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=search_credential,
)
project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
embeddings_client = project_client.inference.get_embeddings_client()

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="insurance-hnsw", kind="hnsw"),
        ExhaustiveKnnAlgorithmConfiguration(name="insurance-eknn", kind="exhaustiveKnn"),
    ],
    profiles=[
        VectorSearchProfile(
            name="insurance-vector-profile",
            algorithm_configuration_name="insurance-hnsw",
        )
    ],
)
semantic_config = SemanticConfiguration(
    name="insurance-semantic",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        content_fields=[SemanticField(field_name="content")],
        keywords_fields=[
            SemanticField(field_name="category"),
            SemanticField(field_name="file_name"),
        ],
    ),
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
    SimpleField(name="processing_date", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="insurance-vector-profile",
    ),
]
index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
)
search_index_client.create_or_update_index(index)


class TextChunker:
    def __init__(self, size: int, overlap: int):
        self.size = size
        self.overlap = overlap

    def clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    def chunk(self, text: str, metadata: Dict) -> List[Dict]:
        text = self.clean_text(text)
        if len(text) <= self.size:
            return [
                {
                    "content": text,
                    "chunk_id": 0,
                    "chunk_count": 1,
                    "metadata": metadata,
                }
            ]
        start = 0
        chunk_id = 0
        chunks: List[Dict] = []
        while start < len(text):
            end = start + self.size
            if end < len(text):
                period = text.rfind(".", start, end)
                if period > start:
                    end = period + 1
            content = text[start:end].strip()
            if content:
                chunks.append(
                    {
                        "content": content,
                        "chunk_id": chunk_id,
                        "chunk_count": 0,
                        "metadata": metadata,
                    }
                )
                chunk_id += 1
            start = max(start + self.size - self.overlap, end)
        for chunk in chunks:
            chunk["chunk_count"] = len(chunks)
        return chunks


chunker = TextChunker(chunk_size, chunk_overlap)
search_documents: List[Dict] = []
container_client = blob_service_client.get_container_client(storage_container)
for blob in container_client.list_blobs():
    if not blob.name.lower().endswith(('.md', '.txt')):
        continue
    blob_client = container_client.get_blob_client(blob)
    text_content = blob_client.download_blob().readall().decode("utf-8")
    if not text_content:
        continue
    metadata: Dict = {
        "file_name": os.path.basename(blob.name),
        "file_type": os.path.splitext(blob.name)[1].lstrip('.') or "text",
        "category": "policies",
    }
    chunks = chunker.chunk(text_content, metadata)
    for chunk in chunks:
        embedding = embeddings_client.embed(
            input=chunk["content"],
            model=embeddings_model,
        )
        search_documents.append(
            {
                "id": str(uuid.uuid4()),
                "title": f"{metadata['file_name']} - Part {chunk['chunk_id'] + 1}",
                "content": chunk["content"],
                "category": metadata["category"],
                "file_name": metadata["file_name"],
                "file_type": metadata["file_type"],
                "chunk_id": chunk["chunk_id"],
                "chunk_count": chunk["chunk_count"],
                "original_length": len(text_content),
                "chunk_length": len(chunk["content"]),
                "processing_date": datetime.utcnow().isoformat() + "Z",
                "content_vector": embedding.data[0].embedding,
            }
        )

batch_size = 50
for start in range(0, len(search_documents), batch_size):
    batch = search_documents[start : start + batch_size]
    search_client.upload_documents(documents=batch)

print(f"Indexed {len(search_documents)} policy chunks into {index_name}.")
