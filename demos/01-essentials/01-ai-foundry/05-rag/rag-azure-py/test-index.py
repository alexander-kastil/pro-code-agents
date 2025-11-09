import os
from typing import Dict, List, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


search_endpoint = os.environ.get("SEARCH_SERVICE_ENDPOINT")
search_key = os.environ.get("SEARCH_ADMIN_KEY")
index_name = os.environ.get("AISEARCH_INDEX_NAME", "insurance-documents-index")
semantic_config_name = os.environ.get("SEMANTIC_CONFIGURATION_NAME", "insurance-semantic")

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_key),
)


def vector_search(query: str, top_k: int = 5, category_filter: Optional[str] = None) -> List[Dict]:
    search_kwargs = {
        "search_text": query,
        "top": top_k,
        "query_type": "semantic",
        "semantic_configuration_name": semantic_config_name,
        "select": [
            "id",
            "title",
            "content",
            "category",
            "file_name",
            "chunk_id",
            "chunk_count",
        ],
    }
    if category_filter:
        search_kwargs["filter"] = f"category eq '{category_filter}'"
    results = search_client.search(**search_kwargs)
    hits: List[Dict] = []
    for result in results:
        hits.append(
            {
                "id": result["id"],
                "title": result.get("title"),
                "content": result.get("content"),
                "category": result.get("category"),
                "file_name": result.get("file_name"),
                "chunk_id": result.get("chunk_id"),
                "chunk_count": result.get("chunk_count"),
                "score": result.get("@search.score", 0.0),
                "reranker_score": result.get("@search.reranker_score", 0.0),
            }
        )
    return hits


def hybrid_search(query: str, top_k: int = 5) -> List[Dict]:
    results = search_client.search(
        search_text=query,
        top=top_k,
        search_mode="all",
        include_total_count=True,
        select=["id", "title", "content", "category", "file_name", "chunk_id"],
    )
    hits: List[Dict] = []
    for result in results:
        hits.append(
            {
                "id": result["id"],
                "title": result.get("title"),
                "content": result.get("content"),
                "category": result.get("category"),
                "file_name": result.get("file_name"),
                "chunk_id": result.get("chunk_id"),
                "score": result.get("@search.score", 0.0),
            }
        )
    return hits


def display_results(query: str, results: List[Dict], label: str) -> None:
    print(f"\n{label} for '{query}'")
    print("=" * 80)
    if not results:
        print("No results found.")
        return
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result['title']}")
        print(f"   Category: {result.get('category')}")
        print(f"   File: {result.get('file_name')} (chunk {result.get('chunk_id', 0) + 1})")
        print(f"   Score: {result.get('score'):.4f}")
        reranker_score = result.get("reranker_score")
        if reranker_score:
            print(f"   Reranker Score: {reranker_score:.4f}")
        preview = result.get("content", "")[:300]
        if result.get("content") and len(result["content"]) > 300:
            preview += "..."
        print(f"   Preview: {preview}")
        print("-" * 80)


sample_queries = [
    "What is covered under collision insurance?",
    "How much does comprehensive coverage cost?",
    "What are the liability limits for commercial vehicles?",
    "Does my policy cover theft and vandalism?",
    "What happens if I hit an uninsured driver?",
    "High value vehicle insurance requirements",
    "Motorcycle insurance coverage options",
]

print(f"Testing index '{index_name}' at {search_endpoint}.")
for query in sample_queries:
    semantic_results = vector_search(query, top_k=3, category_filter="policies")
    display_results(query, semantic_results, "Semantic Search Results")
    hybrid_results = hybrid_search(query, top_k=2)
    display_results(query, hybrid_results, "Hybrid Search Results")
