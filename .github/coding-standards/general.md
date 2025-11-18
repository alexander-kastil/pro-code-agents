# General Coding Standards

## Overview

This document provides general coding standards that apply across all technologies in the Pro Code Agents repository. For technology-specific standards, refer to the specialized documents.

## Code Organization

### File Naming

- **Python**: Use lowercase with underscores (snake_case)
  - Files: `agent_basics.py`, `search_index_manager.py`
  - Modules: `utils/`, `plugins/`
  
- **C#**: Use PascalCase
  - Files: `AgentRunner.cs`, `SearchIndexManager.cs`
  - Folders: `Models/`, `Services/`, `Plugins/`

- **TypeScript/JavaScript**: Use camelCase for files, PascalCase for components
  - Files: `agentService.ts`, `searchUtils.ts`
  - Components: `ChatComponent.tsx`

### Project Structure

Maintain consistent structure across similar projects:

```
project-name/
├── readme.md              # Always lowercase
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Python project metadata (if using uv)
├── .env.copy             # Template for environment variables
├── .gitignore            # Git ignore patterns
├── src/                  # Source code
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
└── assets/               # Static assets (images, documents)
```

## Documentation Standards

### README Files

Always use lowercase `readme.md` (never `README.md`):

```markdown
# Project Name

## Description

Brief description of what the project does.

## Prerequisites

- Python 3.10+ / .NET 8.0+
- Azure AI Foundry project
- Required API keys

## Setup

1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Run the application

## Configuration

Document all required configuration variables.

## Usage

Show example usage with code samples.

## Additional Resources

- Links to relevant documentation
```

### Code Comments

#### When to Comment

- **DO Comment**:
  - Complex algorithms or business logic
  - Non-obvious design decisions
  - Azure-specific patterns that may be unfamiliar
  - Educational explanations for learning purposes

- **DON'T Comment**:
  - Obvious code (e.g., `# Create a variable`)
  - Code that can be made self-documenting with better naming
  - Redundant explanations of what the code literally does

#### Python Docstrings

```python
def process_document(
    file_path: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:
    """
    Process a document by splitting it into overlapping chunks.
    
    This function reads a document and splits it into chunks suitable
    for embedding and vector search operations.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of each chunk in characters (default: 1000)
        overlap: Number of overlapping characters between chunks (default: 200)
    
    Returns:
        List of text chunks
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If chunk_size <= overlap
    
    Example:
        >>> chunks = process_document("document.txt", chunk_size=500)
        >>> len(chunks)
        10
    """
    # Implementation
    pass
```

#### C# XML Documentation

```csharp
/// <summary>
/// Processes a document by splitting it into overlapping chunks.
/// </summary>
/// <param name="filePath">Path to the document file</param>
/// <param name="chunkSize">Size of each chunk in characters</param>
/// <param name="overlap">Number of overlapping characters between chunks</param>
/// <returns>List of text chunks</returns>
/// <exception cref="FileNotFoundException">Thrown when the file doesn't exist</exception>
/// <exception cref="ArgumentException">Thrown when chunkSize is less than or equal to overlap</exception>
/// <example>
/// <code>
/// var chunks = ProcessDocument("document.txt", chunkSize: 500);
/// Console.WriteLine($"Created {chunks.Count} chunks");
/// </code>
/// </example>
public List<string> ProcessDocument(
    string filePath,
    int chunkSize = 1000,
    int overlap = 200)
{
    // Implementation
}
```

## Configuration Management

### Python: .env Files

**ALWAYS** use `.env` files for Python projects:

**.env.copy (template):**
```bash
# Azure AI Foundry
PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
MODEL_DEPLOYMENT=gpt-4

# Azure OpenAI (for embeddings)
AZURE_AI_MODELS_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_AI_MODELS_KEY=

# Application Settings
LOG_LEVEL=INFO
```

**Loading configuration:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")
```

### C#: appsettings.json

**ALWAYS** use `appsettings.json` for C# projects:

**appsettings.json:**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  },
  "AzureAI": {
    "ProjectEndpoint": "https://your-project.services.ai.azure.com/api/projects/your-project",
    "ModelDeployment": "gpt-4",
    "EmbeddingsModel": "text-embedding-ada-002"
  },
  "Application": {
    "Name": "MyAgent",
    "Version": "1.0.0"
  }
}
```

**Loading configuration:**
```csharp
using Microsoft.Extensions.Configuration;

IConfiguration configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json", optional: false)
    .Build();

var endpoint = configuration["AzureAI:ProjectEndpoint"];
var model = configuration["AzureAI:ModelDeployment"];
```

**DO NOT** use:
- Environment variables
- User secrets
- Hardcoded values

## Error Handling

### Minimal Error Handling for Demos

Keep error handling simple and educational:

```python
# Good - Simple and clear
try:
    result = process_data(input)
except FileNotFoundError as e:
    print(f"Error: File not found - {e}")
    raise
except Exception as e:
    print(f"Unexpected error: {e}")
    raise

# Avoid - Too complex for demo code
try:
    result = process_data(input)
except FileNotFoundError as e:
    logger.error(f"File not found: {e}", exc_info=True)
    send_error_notification(e)
    retry_with_backup(input)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return default_value
except (NetworkError, TimeoutError) as e:
    logger.error(f"Network issue: {e}")
    queue_for_retry(input)
except Exception as e:
    logger.critical(f"Critical error: {e}", exc_info=True)
    emergency_shutdown()
```

### When to Add Error Handling

- **Always**: For external API calls (Azure services)
- **Usually**: For file operations
- **Sometimes**: For user input validation
- **Rarely**: For pure computational logic (unless complex)

## Dependency Management

### Python

**Use both requirements.txt and pyproject.toml:**

**requirements.txt:**
```txt
azure-ai-projects>=1.0.0
azure-ai-inference>=1.0.0
azure-identity>=1.15.0
python-dotenv>=1.0.0
```

**pyproject.toml:**
```toml
[project]
name = "agent-basics"
version = "0.1.0"
description = "Basic agent examples using Azure AI Foundry"
requires-python = ">=3.10"

dependencies = [
    "azure-ai-projects>=1.0.0",
    "azure-ai-inference>=1.0.0",
    "azure-identity>=1.15.0",
    "python-dotenv>=1.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
]
```

**Installing dependencies:**
```bash
# Using uv (preferred)
uv pip install -r requirements.txt
# or
uv sync

# Using pip
pip install -r requirements.txt
```

### C#

**.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Azure.AI.Projects" Version="1.0.0" />
    <PackageReference Include="Azure.AI.Inference" Version="1.0.0" />
    <PackageReference Include="Azure.Identity" Version="1.11.0" />
    <PackageReference Include="Microsoft.Extensions.Configuration" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="8.0.0" />
  </ItemGroup>
</Project>
```

**Installing dependencies:**
```bash
dotnet restore
```

## Version Control

### .gitignore

Standard patterns to ignore:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
*.egg-info/
.pytest_cache/
uv.lock

# C#
bin/
obj/
*.user
*.suo
.vs/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Azure
.azure/
local.settings.json

# Sensitive data
*.key
*.pem
appsettings.Development.json
```

### Git Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add file search capability to agent-basics example"
git commit -m "Fix: Handle missing environment variables gracefully"
git commit -m "Update documentation for MCP server setup"

# Avoid
git commit -m "update"
git commit -m "fix stuff"
git commit -m "changes"
```

## Testing

### Python Testing

Use pytest for testing:

```python
# test_agent.py
import pytest
from agent_basics import create_agent

def test_create_agent():
    """Test agent creation with valid configuration."""
    agent = create_agent()
    assert agent is not None
    assert agent.name == "basic-agent"

def test_create_agent_with_custom_name():
    """Test agent creation with custom name."""
    agent = create_agent(name="custom-agent")
    assert agent.name == "custom-agent"
```

Run tests:
```bash
pytest tests/
```

### C# Testing

Use xUnit for testing:

```csharp
using Xunit;

public class AgentTests
{
    [Fact]
    public void CreateAgent_WithValidConfig_ReturnsAgent()
    {
        // Arrange
        var config = TestConfig.GetValid();
        
        // Act
        var agent = AgentFactory.Create(config);
        
        // Assert
        Assert.NotNull(agent);
        Assert.Equal("basic-agent", agent.Name);
    }
}
```

Run tests:
```bash
dotnet test
```

## Performance Considerations

### Async/Await

Use async patterns consistently:

**Python:**
```python
async def process_multiple_requests(requests: List[str]) -> List[str]:
    """Process multiple requests concurrently."""
    tasks = [process_request(req) for req in requests]
    return await asyncio.gather(*tasks)
```

**C#:**
```csharp
public async Task<List<string>> ProcessMultipleRequestsAsync(
    List<string> requests)
{
    var tasks = requests.Select(req => ProcessRequestAsync(req));
    return (await Task.WhenAll(tasks)).ToList();
}
```

### Resource Cleanup

Always clean up resources:

**Python:**
```python
# Use context managers
async with AIProjectClient(endpoint=endpoint, credential=credential) as client:
    # Use client
    pass
# Client automatically closed
```

**C#:**
```csharp
// Use using statements
await using var client = new AIProjectClient(new Uri(endpoint), credential);
// Use client
// Client automatically disposed
```

## Security Best Practices

1. **Never Commit Secrets**
   - Use `.env.copy` or `appsettings.json` templates with empty values
   - Add actual secrets files to `.gitignore`

2. **Use Managed Identities**
   - Prefer `DefaultAzureCredential` over API keys
   - Use Azure CLI authentication for development

3. **Validate Inputs**
   - Validate all user inputs before processing
   - Sanitize data before sending to AI models

4. **Content Filtering**
   - Use Azure AI Content Safety when appropriate
   - Implement appropriate content moderation

## Educational Focus

Remember that this is a training repository:

### Principles

1. **Clarity Over Cleverness**: Write code that's easy to understand
2. **Progressive Complexity**: Start simple, then show advanced patterns
3. **Practical Examples**: Use realistic scenarios
4. **Complete Samples**: Show full, working examples
5. **Explain Why**: Don't just show what, explain why

### Code Style

```python
# Good - Clear and educational
def calculate_chunk_size(document_length: int, target_chunks: int) -> int:
    """
    Calculate optimal chunk size for a document.
    
    We divide the document into roughly equal chunks to ensure
    consistent processing across the entire document.
    """
    return document_length // target_chunks

# Avoid - Too terse for educational purposes
calc_size = lambda d, t: d // t
```

## Summary

- Use consistent file naming and project structure
- Write clear documentation with proper readme files
- Manage configuration with .env (Python) or appsettings.json (C#)
- Keep error handling minimal and educational
- Maintain synchronized dependency files
- Follow security best practices
- Focus on clarity and educational value
