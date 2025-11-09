import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

# Load environment variables
load_dotenv()

# Simple configuration variables at the top
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AISEARCH_INDEX_NAME = os.environ.get("AISEARCH_INDEX_NAME")
EMBEDDINGS_MODEL = os.environ.get("EMBEDDINGS_MODEL")

# create a project client using environment variables loaded from the .env file
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential()
)

# create a vector embeddings client that will be used to generate vector embeddings
embeddings = project.inference.get_embeddings_client()

# use the project client to get the default search connection
search_connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_AI_SEARCH, include_credentials=True
)

# Create a search client using the search connection
search_client = SearchClient(
    endpoint=search_connection.endpoint_url,
    index_name=AISEARCH_INDEX_NAME,
    credential=AzureKeyCredential(key=search_connection.key),
)


def test_vector_search(query: str, top: int = 3):
    """
    Test vector search using embeddings.
    This performs a pure vector similarity search.
    """
    print(f"\n🔍 Testing Vector Search for: '{query}'")
    print("=" * 80)
    
    # Generate embedding for the query
    embedding = embeddings.embed(model=EMBEDDINGS_MODEL, input=query)
    search_vector = embedding.data[0].embedding
    
    # Create vector query
    vector_query = VectorizedQuery(
        vector=search_vector, 
        k_nearest_neighbors=top, 
        fields="contentVector"
    )
    
    # Perform vector search
    results = search_client.search(
        search_text=None,  # Pure vector search, no text
        vector_queries=[vector_query],
        select=["id", "title", "content"],
        top=top
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Score: {result['@search.score']:.4f}")
        print(f"   Content: {result['content'][:200]}...")
    
    print("\n" + "=" * 80)


def test_hybrid_search(query: str, top: int = 3):
    """
    Test hybrid search combining vector and keyword search.
    This combines semantic similarity with traditional text matching.
    """
    print(f"\n🔍 Testing Hybrid Search for: '{query}'")
    print("=" * 80)
    
    # Generate embedding for the query
    embedding = embeddings.embed(model=EMBEDDINGS_MODEL, input=query)
    search_vector = embedding.data[0].embedding
    
    # Create vector query
    vector_query = VectorizedQuery(
        vector=search_vector, 
        k_nearest_neighbors=top, 
        fields="contentVector"
    )
    
    # Perform hybrid search (vector + text)
    results = search_client.search(
        search_text=query,  # Text query for keyword matching
        vector_queries=[vector_query],  # Vector query for semantic matching
        select=["id", "title", "content"],
        top=top
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Score: {result['@search.score']:.4f}")
        print(f"   Content: {result['content'][:200]}...")
    
    print("\n" + "=" * 80)


def test_semantic_search(query: str, top: int = 3):
    """
    Test semantic search with semantic ranking.
    This uses Azure's semantic ranker for improved relevance.
    """
    print(f"\n🔍 Testing Semantic Search for: '{query}'")
    print("=" * 80)
    
    # Generate embedding for the query
    embedding = embeddings.embed(model=EMBEDDINGS_MODEL, input=query)
    search_vector = embedding.data[0].embedding
    
    # Create vector query
    vector_query = VectorizedQuery(
        vector=search_vector, 
        k_nearest_neighbors=50,  # Get more candidates for reranking
        fields="contentVector"
    )
    
    # Perform semantic search
    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["id", "title", "content"],
        query_type="semantic",
        semantic_configuration_name="default",
        top=top
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Score: {result['@search.score']:.4f}")
        if '@search.reranker_score' in result:
            print(f"   Reranker Score: {result['@search.reranker_score']:.4f}")
        print(f"   Content: {result['content'][:200]}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Azure AI Search index with vector, hybrid, and semantic search")
    parser.add_argument(
        "--query",
        type=str,
        help="Search query to test",
        default="I need a new tent for 4 people, what would you recommend?"
    )
    parser.add_argument(
        "--top",
        type=int,
        help="Number of results to return",
        default=3
    )
    parser.add_argument(
        "--search-type",
        type=str,
        choices=["vector", "hybrid", "semantic", "all"],
        help="Type of search to test",
        default="all"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"Testing Azure AI Search Index: {AISEARCH_INDEX_NAME}")
    print(f"{'='*80}")
    
    if args.search_type in ["vector", "all"]:
        test_vector_search(args.query, args.top)
    
    if args.search_type in ["hybrid", "all"]:
        test_hybrid_search(args.query, args.top)
    
    if args.search_type in ["semantic", "all"]:
        test_semantic_search(args.query, args.top)
    
    print(f"\n✅ Search testing completed!\n")
