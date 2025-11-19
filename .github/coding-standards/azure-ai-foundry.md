# Azure AI Foundry Coding Standards

## Overview

This document provides coding standards for working with Azure AI Foundry projects, including SDK usage, model interactions, and RAG implementations.

## Python Standards

### Environment Configuration

**ALWAYS** use `.env` files for configuration in Python projects:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")
```

Required environment variables:
- `PROJECT_ENDPOINT`: Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT`: Name of the deployed model
- `AZURE_AI_MODELS_ENDPOINT`: Azure OpenAI endpoint (for embeddings)
- `AZURE_AI_MODELS_KEY`: API key (when not using managed identity)

### Azure AI Projects SDK

#### Client Initialization

Use `DefaultAzureCredential` for authentication:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)
```

#### Async Pattern

For async operations, use async clients and context managers:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

async with DefaultAzureCredential() as credential:
    async with AIProjectClient(
        endpoint=endpoint,
        credential=credential
    ) as project_client:
        # Your async code here
        pass
```

### Azure AI Inference SDK

#### Chat Completions

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage

messages = [
    UserMessage(content="Your prompt here")
]

response = client.complete(
    model=model_deployment,
    messages=messages
)
```

#### Streaming Responses

```python
response = client.complete(
    model=model_deployment,
    messages=messages,
    stream=True
)

for chunk in response:
    if chunk.choices:
        print(chunk.choices[0].delta.content, end="")
```

### RAG Implementation Patterns

#### Search Index Configuration

```python
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)

# Define index schema with vector search
fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="content", type="Edm.String"),
    SearchField(
        name="embedding",
        type="Collection(Edm.Single)",
        vector_search_dimensions=1536,
        vector_search_profile_name="myHnswProfile"
    )
]
```

#### Document Processing

```python
from typing import List, Dict

def chunk_document(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split document into overlapping chunks.
    
    Args:
        text: Document text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks
```

### Error Handling

Keep error handling minimal for demo code:

```python
try:
    response = client.complete(model=model, messages=messages)
except Exception as e:
    print(f"Error: {e}")
    raise
```

Avoid excessive try-catch blocks that obscure the main logic.

## C# Standards

### Configuration Management

**ALWAYS** use `appsettings.json` for configuration:

```json
{
  "AzureConfig": {
    "ProjectEndpoint": "https://your-project.services.ai.azure.com/api/projects/your-project",
    "ModelDeployment": "gpt-4",
    "EmbeddingsModel": "text-embedding-ada-002",
    "AzureAIModelsEndpoint": "https://your-resource.openai.azure.com/",
    "AzureAIModelsKey": ""
  }
}
```

Load configuration:

```csharp
using Microsoft.Extensions.Configuration;

IConfiguration configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json", optional: false)
    .Build();

var config = new AzureConfiguration();
configuration.GetSection("AzureConfig").Bind(config);
```

**DO NOT** use environment variables or user secrets in this repository.

### Client Initialization

```csharp
using Azure.Identity;
using Azure.AI.Projects;

var credential = new DefaultAzureCredential();
var projectClient = new AIProjectClient(
    new Uri(endpoint),
    credential
);
```

### Azure AI Inference

```csharp
using Azure.AI.Inference;

var chatClient = new ChatCompletionsClient(
    new Uri(endpoint),
    new AzureKeyCredential(apiKey)
);

var messages = new List<ChatMessage>
{
    new UserMessage("Your prompt here")
};

var response = await chatClient.CompleteAsync(
    model: modelDeployment,
    messages: messages
);
```

### Async/Await Patterns

Always use async/await for Azure SDK calls:

```csharp
public async Task<string> GetCompletionAsync(string prompt)
{
    var messages = new List<ChatMessage>
    {
        new UserMessage(prompt)
    };
    
    var response = await chatClient.CompleteAsync(
        model: modelDeployment,
        messages: messages
    );
    
    return response.Value.Choices[0].Message.Content;
}
```

### RAG Implementation

```csharp
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

public class SearchIndexManager
{
    private readonly SearchIndexClient _indexClient;
    
    public async Task<SearchIndex> CreateIndexAsync(string indexName)
    {
        var definition = new SearchIndex(indexName)
        {
            Fields =
            {
                new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
                new SearchableField("content") { IsFilterable = true },
                new SearchField("embedding", SearchFieldDataType.Collection(SearchFieldDataType.Single))
                {
                    VectorSearchDimensions = 1536,
                    VectorSearchProfileName = "myHnswProfile"
                }
            }
        };
        
        return await _indexClient.CreateIndexAsync(definition);
    }
}
```

## Best Practices

### Code Organization

1. **Single Responsibility**: Each file should have a clear, single purpose
2. **Descriptive Naming**: Use clear, descriptive names for variables and functions
3. **Type Hints (Python)**: Use type hints for function parameters and return values
4. **XML Docs (C#)**: Add XML documentation comments for public APIs

### Educational Focus

- Write code that demonstrates concepts clearly
- Add comments only when explaining complex or non-obvious logic
- Keep examples focused and concise
- Avoid production-level patterns that obscure the learning objective

### Performance Considerations

- Use streaming for long-running completions
- Implement caching for repeated embeddings
- Batch operations when possible

### Security

- Never commit API keys or secrets to source control
- Use `.env.copy` templates to show required variables
- Use managed identities (DefaultAzureCredential) when possible
