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

3. Edit `.env` and set your `PROJECT_ENDPOINT`, `AISEARCH_INDEX_NAME`, `INTENT_MAPPING_MODEL`, `EMBEDDINGS_MODEL`, and `EVALUATION_MODEL`:

   ```
   PROJECT_ENDPOINT=https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name
   AISEARCH_INDEX_NAME=product-index
   INTENT_MAPPING_MODEL=gpt-4.1-mini
   EMBEDDINGS_MODEL=text-embedding-3-small
   EVALUATION_MODEL=gpt-4.1-mini
   ```

4. Create the search index:

   ```bash
   uv run python create_search_index.py
   ```

5. Load product documents:
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
