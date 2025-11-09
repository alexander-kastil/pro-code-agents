# Build a custom chat app with the Azure AI Foundry SDK

[Build a custom chat app with the Azure AI Foundry SDK](https://learn.microsoft.com/en-us/azure/ai-studio/tutorials/copilot-sdk-create-resources?tabs=windows)

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Copy the template and configure your environment:

   ```bash
   cp .env.copy .env
   ```

3. Edit `.env` and set your `PROJECT_ENDPOINT`, `AISEARCH_INDEX_NAME`, `INTENT_MAPPING_MODEL`, `EMBEDDINGS_MODEL`, `EVALUATION_MODEL`, and Azure Search credentials:

   ```
   PROJECT_ENDPOINT=https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name
   AISEARCH_INDEX_NAME=product-index
   INTENT_MAPPING_MODEL=gpt-4.1-mini
   EMBEDDINGS_MODEL=text-embedding-3-small
   EVALUATION_MODEL=gpt-4.1-mini
   STORAGE_CONNECTION_STRING=your_storage_connection_string
   SEARCH_SERVICE_NAME=your_search_service_name
   SEARCH_SERVICE_ENDPOINT=https://your-search-service.search.windows.net
   SEARCH_ADMIN_KEY=your_search_admin_key
   ```

4. Create the vectorized index (for insurance documents):

   ```bash
   uv run python create_vectorized_index.py
   ```

   This script creates an Azure AI Search index with pre-computed embeddings for insurance policy documents.

5. Create the search index:

   ```bash
   uv run python create_search_index.py
   ```

6. Load product documents:
   ```bash
   uv run python get_product_documents.py
   ```

## Test with prompt:

```bash
uv run python chat_with_products.py --query "I need a new tent for 4 people, what would you recommend?"
```

## Test with logging:

```bash
uv run python chat_with_products.py --query "I need a new tent for 4 people, what would you recommend?" --enable-telemetry
```

## Run evaluations:

```bash
uv run python evaluate.py
```

## Document Vectorization

The `create_vectorized_index.py` script implements the document vectorization workflow from the `2.document-vectorization.ipynb` notebook. It performs the following steps:

1. **Initialize Azure Services**: Connect to Azure Blob Storage, Azure AI Search, and Azure AI Projects
2. **Create Search Index**: Set up an Azure AI Search index with vector search and semantic search capabilities
3. **Retrieve Documents**: Download processed insurance documents from Azure Blob Storage
4. **Process Documents**: Chunk documents into optimally-sized pieces with overlapping content
5. **Generate Embeddings**: Create vector embeddings using Azure AI Projects embeddings client
6. **Upload Documents**: Index the documents with their embeddings in Azure AI Search
7. **Test Search**: Validate the index with sample insurance-related queries

The script processes only policy documents from the `processed-documents` container and creates a searchable index with both semantic and vector search capabilities.
