import os
from typing import List, Dict

# Azure SDK imports
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# Simple configuration variables at the top
search_endpoint = os.environ.get("SEARCH_SERVICE_ENDPOINT")
search_key = os.environ.get("SEARCH_ADMIN_KEY")
search_index_name = "insurance-documents-index"

# Initialize search client
search_credential = AzureKeyCredential(search_key)
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index_name,
    credential=search_credential
)

print(f"✅ Connected to search index: {search_index_name}")

# Step 7: Test the Search Index
def vector_search(query: str, top_k: int = 5, category_filter: str = None) -> List[Dict]:
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
    
    results = search_client.search(**search_params)
    
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

def hybrid_search(query: str, top_k: int = 5) -> List[Dict]:
    results = search_client.search(
        search_text=query,
        top=top_k,
        search_mode="all",
        include_total_count=True,
        select=["id", "title", "content", "category", "file_name", "chunk_id"]
    )
    
    search_results = []
    for result in results:
        search_results.append({
            'id': result['id'],
            'title': result['title'],
            'content': result['content'],
            'category': result['category'],
            'file_name': result['file_name'],
            'chunk_id': result['chunk_id'],
            'score': result.get('@search.score', 0)
        })
    
    return search_results

def display_search_results(query: str, results: List[Dict], search_type: str = "Search"):
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

# Test queries
test_queries = [
    "What is covered under collision insurance?",
    "How much does comprehensive coverage cost?",
    "What are the liability limits for commercial vehicles?",
    "Does my policy cover theft and vandalism?",
    "What happens if I hit an uninsured driver?",
    "High value vehicle insurance requirements",
    "Motorcycle insurance coverage options"
]

print("🧪 Testing Azure AI Search...")
print("=" * 80)

for query in test_queries:
    print(f"\n\n🔍 Testing query: '{query}'")
    
    results = vector_search(query, top_k=3)
    
    if results:
        print(f"✅ Found {len(results)} relevant chunks")
        display_search_results(query, results, "Semantic Search")
    else:
        print("❌ No relevant documents found")
    
    print("-" * 40)

print("\n✅ Query testing completed!")

# Interactive search function
def interactive_search():
    print("\n🔍 Interactive Azure AI Search Interface")
    print("=" * 50)
    print("Enter your search queries (type 'quit' to exit)")
    print("Optional commands:")
    print("  - Add 'category:policies' or 'category:claims' to filter results")
    print("  - Use natural language queries for best semantic search results")
    print()
    
    while True:
        query = input("\n🔍 Search: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        category_filter = None
        if 'category:' in query:
            parts = query.split('category:')
            query = parts[0].strip()
            category_filter = parts[1].strip()
        
        print(f"\n🧠 Performing semantic search...")
        results = vector_search(query, top_k=5, category_filter=category_filter)
        
        display_search_results(query, results, "Semantic Search")
        
        print(f"\n🔄 Hybrid search results:")
        hybrid_results = hybrid_search(query, top_k=3)
        if hybrid_results:
            for i, result in enumerate(hybrid_results[:2], 1):
                print(f"{i}. {result['title']} (Score: {result['score']:.4f})")
    
    print("\n👋 Search session ended")

# Uncomment to run interactive search
# interactive_search()
