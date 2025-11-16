# TODO: agents-ai-search-rag.py

## Issue

The agent requires a model that supports Azure AI Search tools. The current model `gpt-5-mini` is not compatible.

**Error Message:**

```
The model 'gpt-5-mini' cannot be used with the following tools: azure_ai_search.
This model only supports Responses API compatible tools.
```

## Required Actions

### 1. Update Model Deployment

Change the `MODEL_DEPLOYMENT` variable in your `.env` file:

```
MODEL_DEPLOYMENT="gpt-4o"
```

or

```
MODEL_DEPLOYMENT="gpt-4"
```

### 2. Configure Azure AI Search

- Create an Azure AI Search index named `insurance-documents-index` in your Azure AI Foundry project
- Upload insurance-related documents to the index
- Verify the Azure AI Search connection is properly configured in your project

### 3. Verify Connection

The agent will automatically retrieve the default Azure AI Search connection from your project:

```python
conn_id = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH).id
```

## Test Command

```bash
python agents-ai-search-rag.py
```

## Expected Behavior

The agent should:

1. Connect to Azure AI Search
2. Create an agent with RAG capabilities
3. Answer the question: "Which policies cover a broken car side mirror?"
4. Return results with citations from the search index
