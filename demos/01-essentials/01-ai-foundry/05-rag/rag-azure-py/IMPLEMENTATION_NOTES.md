# Azure AI Search RAG Implementation

This implementation creates a RAG (Retrieval-Augmented Generation) solution using Azure AI Search based on the notebook `2.document-vectorization.ipynb`.

## Files Created

### 1. create_search_index.py
This script implements Steps 2-6 from the notebook:

- **Step 2: Initialize Azure Clients**
  - Blob Storage Client (for document retrieval)
  - Search Index Client (for index management)
  - Search Client (for document upload)
  - Azure AI Project Client (for embeddings generation)

- **Step 3: Create Azure AI Search Index**
  - Index schema with fields for content, metadata, and vector embeddings
  - Vector search configuration with HNSW and Exhaustive KNN algorithms
  - Semantic search configuration for natural language queries
  - Index name: `insurance-documents-index`

- **Step 4: Text Chunking**
  - Chunk size: 1000 characters
  - Overlap: 200 characters
  - Smart chunking at sentence boundaries

- **Step 5: Retrieve Documents**
  - Downloads processed documents from blob storage container `processed-documents`
  - Processes only policy documents as requested
  - Filters for successfully processed documents

- **Step 6: Upload to Azure AI Search**
  - Generates embeddings using Azure AI Project
  - Uploads documents in batches of 50
  - Creates searchable chunks with vector embeddings

### 2. test-index.py
This script implements Step 7 from the notebook:

- **Semantic Search**: Natural language queries with reranking
- **Hybrid Search**: Combines keyword and vector search
- **Predefined Test Queries**: Insurance-related sample queries
- **Interactive Search**: Command-line interface for testing
- **Formatted Results**: Displays scores, content previews, and metadata

## Configuration

Simple environment variable configuration at the top of each script:

```python
# In create_search_index.py
conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
search_endpoint = os.environ.get("SEARCH_SERVICE_ENDPOINT")
search_key = os.environ.get("SEARCH_ADMIN_KEY")
project_endpoint = os.environ.get("PROJECT_ENDPOINT")
embeddings_model = os.environ.get("EMBEDDINGS_MODEL", "text-embedding-ada-002")
```

## Usage

1. Ensure your `.env` file has the required variables:
   - `STORAGE_CONNECTION_STRING`
   - `SEARCH_SERVICE_ENDPOINT`
   - `SEARCH_ADMIN_KEY`
   - `PROJECT_ENDPOINT`
   - `EMBEDDINGS_MODEL`

2. Run the index creation script:
   ```bash
   python create_search_index.py
   ```

3. Test the index:
   ```bash
   python test-index.py
   ```

## Design Decisions

### Why Step 2 is included
Step 2 initializes the Azure clients which are required for all subsequent operations. Without it, Steps 3-6 cannot function.

### Simple approach
- No error handling (as requested)
- No config classes (as requested)
- Direct environment variable access
- Straightforward implementation following the notebook structure

### Only policy documents
The implementation processes only policy documents from the blob storage, filtering out other document types.

## Next Steps

After running these scripts, you can:
- Use the search index in your AI agents
- Integrate with Azure AI Chat completion
- Build a copilot application using the indexed documents
