# Model Context Protocol (MCP) Development Standards

## Overview

This document provides coding standards for developing MCP servers using Python and C#. MCP servers expose tools and resources that can be used by AI agents.

## Python Standards

### MCP Server Structure

Use the FastMCP framework for Python MCP servers:

```python
from fastmcp import FastMCP

# Initialize FastMCP server with a descriptive name
mcp = FastMCP("your-server-name")
```

### Tool Definition

Define tools using the `@mcp.tool()` decorator:

```python
@mcp.tool()
def your_tool_name(
    param1: str,
    param2: int = 10,
) -> str:
    """Tool description that explains what the tool does.
    
    This description is shown to the AI agent and helps it understand
    when and how to use this tool.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default value
        
    Returns:
        Description of what the tool returns
        
    Raises:
        ValueError: When invalid input is provided
    """
    # Tool implementation
    return "result"
```

### Environment Configuration

Use environment variables for sensitive configuration:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
```

### Error Handling

Provide clear error messages that help the AI agent understand what went wrong:

```python
@mcp.tool()
def process_data(data: str) -> str:
    """Process the provided data."""
    if not data:
        raise ValueError("Data parameter cannot be empty")
    
    try:
        result = perform_operation(data)
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to process data: {str(e)}")
```

### Logging

Use Python's built-in logging module:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def example_tool(input: str) -> str:
    """Example tool with logging."""
    logger.info(f"Processing input: {input}")
    result = process(input)
    logger.info(f"Completed processing, result length: {len(result)}")
    return result
```

### Complete Example: YouTube Transcriber MCP Server

```python
"""YouTube Transcription MCP Server

This MCP server provides tools for transcribing YouTube videos.
"""

import logging
from urllib.parse import urlparse, parse_qs

from fastmcp import FastMCP
from langchain_community.document_loaders import YoutubeLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("youtube-transcriber")


def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        The extracted video ID
        
    Raises:
        ValueError: If the URL is not a valid YouTube URL
    """
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
    
    raise ValueError(f"Not a valid YouTube URL: {url}")


@mcp.tool()
def get_youtube_transcription(
    url: str,
    language: str = "en",
) -> str:
    """Get the transcription of a YouTube video.
    
    Args:
        url: The YouTube video URL
        language: The language code for the transcript (default: "en")
        
    Returns:
        The video transcription as a string
        
    Raises:
        ValueError: If the URL is invalid or transcription is unavailable
    """
    try:
        video_id = extract_video_id(url)
        logger.info(f"Fetching transcript for video ID: {video_id}")
        
        loader = YoutubeLoader(video_id, language=[language])
        docs = loader.load()
        
        if not docs:
            raise ValueError(f"No transcript available for video: {url}")
        
        transcript = "\n\n".join(doc.page_content for doc in docs)
        logger.info(f"Successfully retrieved transcript ({len(transcript)} chars)")
        
        return transcript
        
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        raise ValueError(f"Failed to get transcript: {str(e)}")
```

### Server Startup Scripts

Provide both PowerShell and Bash startup scripts:

**start.ps1:**
```powershell
# Start MCP server for Windows
Write-Host "Starting YouTube Transcriber MCP Server..." -ForegroundColor Green

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
}

# Run the server
python -m fastmcp run server:mcp
```

**start.sh:**
```bash
#!/bin/bash
echo "Starting YouTube Transcriber MCP Server..."

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the server
python -m fastmcp run server:mcp
```

### Dependencies

Use both `requirements.txt` and `pyproject.toml`:

**requirements.txt:**
```txt
fastmcp
python-dotenv
langchain-community
```

**pyproject.toml:**
```toml
[project]
name = "youtube-transcriber-mcp"
version = "0.1.0"
description = "MCP server for YouTube video transcription"
requires-python = ">=3.10"

dependencies = [
    "fastmcp",
    "python-dotenv",
    "langchain-community",
]
```

## C# Standards

### Project Structure

Create a console application for MCP servers:

```csharp
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.Extensions.Configuration" Version="8.0.0" />
    <PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="8.0.0" />
  </ItemGroup>
</Project>
```

### MCP Server Implementation

```csharp
using System.Text.Json;
using Microsoft.Extensions.Configuration;

namespace YourMcpServer;

public class McpServer
{
    private readonly IConfiguration _configuration;
    
    public McpServer()
    {
        _configuration = new ConfigurationBuilder()
            .AddJsonFile("appsettings.json", optional: false)
            .Build();
    }
    
    /// <summary>
    /// Your tool description.
    /// </summary>
    /// <param name="input">Description of input parameter</param>
    /// <returns>Description of return value</returns>
    public async Task<string> YourToolAsync(string input)
    {
        // Tool implementation
        return await ProcessInputAsync(input);
    }
}
```

### Configuration

Use `appsettings.json` for all configuration:

```json
{
  "McpConfig": {
    "ServerName": "your-mcp-server",
    "ApiEndpoint": "https://api.example.com",
    "ApiKey": ""
  }
}
```

### Tool Registration

```csharp
public class ToolRegistry
{
    private readonly Dictionary<string, Func<string, Task<string>>> _tools = new();
    
    public void RegisterTool(string name, Func<string, Task<string>> handler)
    {
        _tools[name] = handler;
    }
    
    public async Task<string> ExecuteToolAsync(string toolName, string input)
    {
        if (!_tools.TryGetValue(toolName, out var handler))
        {
            throw new ArgumentException($"Unknown tool: {toolName}");
        }
        
        return await handler(input);
    }
}
```

## Best Practices

### Tool Design

1. **Clear Purpose**: Each tool should have a single, well-defined purpose
2. **Descriptive Names**: Use verb-based names (e.g., `get_`, `create_`, `update_`)
3. **Comprehensive Descriptions**: Write detailed docstrings that help the AI understand when to use the tool
4. **Input Validation**: Validate all inputs and provide clear error messages

### Error Messages

Write error messages that are helpful to both developers and AI agents:

```python
# Good
raise ValueError("URL must start with 'https://www.youtube.com/' or 'https://youtu.be/'")

# Bad
raise ValueError("Invalid URL")
```

### Documentation

Each MCP server should have a comprehensive `readme.md`:

```markdown
# Your MCP Server Name

## Description

Brief description of what the MCP server does.

## Tools

### tool_name

Description of the tool.

**Parameters:**
- `param1` (string, required): Description
- `param2` (int, optional, default: 10): Description

**Returns:**
- string: Description of return value

**Example:**
```json
{
  "tool": "tool_name",
  "params": {
    "param1": "value"
  }
}
```

## Setup

1. Install dependencies
2. Configure environment variables
3. Start the server

## Configuration

Required environment variables:
- `API_KEY`: Your API key
```

### Testing

Provide example usage in the readme:

```python
# Example usage
if __name__ == "__main__":
    # Test the tool directly
    result = get_youtube_transcription(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        language="en"
    )
    print(result)
```

### Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate and sanitize all inputs
- Implement rate limiting when calling external APIs
