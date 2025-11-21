# Azure AI Agents SDK Migration Guide

## Overview

This guide documents the migration from `azure-ai-projects` (`AIProjectClient.agents`) to `azure-ai-agents` (`AgentsClient`) API patterns for Azure AI Agent applications.

**Affected SDK Versions:**

- **Old (Deprecated)**: `azure-ai-projects <= 2.0.0b1`
- **New (Required)**: `azure-ai-agents >= 1.2.0b6`, `azure-ai-projects >= 2.0.0b2`

---

## Breaking Changes Summary

### 1. Client Instantiation Pattern

#### ❌ Old (Deprecated)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents
    agent = agents_client.create_agent(...)
```

#### ✅ New (Required)

```python
from azure.ai.agents import AgentsClient
from azure.ai.projects import AIProjectClient  # Still needed for connections
from azure.identity import DefaultAzureCredential

# Keep AIProjectClient for connection management
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# Create separate AgentsClient for agent operations
agents_client = AgentsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

with agents_client:
    agent = agents_client.create_agent(...)
```

**Key Points:**

- `AgentsClient` is now a standalone client, not accessed via `project_client.agents`
- `AIProjectClient` is still needed for connection management (e.g., `project_client.connections.get()`)
- Use `with agents_client:` for context management

---

### 2. Import Changes

#### ❌ Old

```python
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, FunctionTool, ToolSet
```

#### ✅ New

```python
from azure.ai.agents import AgentsClient
from azure.ai.projects import AIProjectClient  # Only for connections
from azure.ai.agents.models import MessageRole, FunctionTool, ToolSet
```

---

### 3. Agent Operations

All agent operations now go directly through `AgentsClient` instead of `project_client.agents.*`

#### ❌ Old

```python
# Creating agent
agent = project_client.agents.create_agent(...)

# Thread operations
thread = project_client.agents.threads.create()
project_client.agents.threads.delete(thread.id)

# Message operations
message = project_client.agents.messages.create(...)
messages = project_client.agents.messages.list(...)

# Run operations
run = project_client.agents.runs.create_and_process(...)
run = project_client.agents.runs.get(...)
project_client.agents.runs.cancel(...)

# Agent deletion
project_client.agents.delete_agent(agent.id)
```

#### ✅ New

```python
# Creating agent
agent = agents_client.create_agent(...)

# Thread operations
thread = agents_client.threads.create()
agents_client.threads.delete(thread.id)

# Message operations
message = agents_client.messages.create(...)
messages = agents_client.messages.list(...)

# Run operations
run = agents_client.runs.create_and_process(...)
run = agents_client.runs.get(...)
agents_client.runs.cancel(...)

# Agent deletion
agents_client.delete_agent(agent.id)
```

---

### 4. Auto Function Calling

#### ❌ Old (Incorrect - caused AttributeError)

```python
with project_client:
    project_client.agents.enable_auto_function_calls(toolset)
    agent = project_client.agents.create_agent(...)
```

#### ✅ New (Correct)

```python
with agents_client:
    agents_client.enable_auto_function_calls(toolset)
    agent = agents_client.create_agent(...)
```

**Note:** `enable_auto_function_calls()` is called on `AgentsClient`, not on `AgentsOperations`.

---

### 5. Message Retrieval (Deprecated Method)

#### ❌ Old (No longer available)

```python
response_message = agents_client.messages.get_last_message_by_role(
    thread_id=thread.id,
    role=MessageRole.AGENT
)
if response_message:
    for text_message in response_message.text_messages:
        print(text_message.text.value)
```

#### ✅ New (Manual iteration)

```python
from azure.ai.agents.models import ListSortOrder

messages = agents_client.messages.list(
    thread_id=thread.id,
    order=ListSortOrder.DESCENDING
)
for message in messages:
    if message.role == MessageRole.AGENT:
        for text_message in message.text_messages:
            print(text_message.text.value)
        break  # Get only the last agent message
```

---

### 6. Windows Console UTF-8 Encoding

Add UTF-8 encoding wrapper to handle emoji characters on Windows:

```python
import io
import sys

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

Add this at the top of your script, after imports.

---

## Migration Checklist

Use this checklist when migrating agent files:

- [ ] **Update imports**: Add `from azure.ai.agents import AgentsClient`
- [ ] **Add UTF-8 encoding**: Add `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`
- [ ] **Create AgentsClient**: Add `agents_client = AgentsClient(endpoint, credential)`
- [ ] **Update context manager**: Change `with project_client:` to `with agents_client:`
- [ ] **Remove nested agents_client**: Delete `agents_client = project_client.agents` line
- [ ] **Replace all `project_client.agents.*`**: Find/replace with `agents_client.*`
  - `project_client.agents.create_agent` → `agents_client.create_agent`
  - `project_client.agents.threads.*` → `agents_client.threads.*`
  - `project_client.agents.messages.*` → `agents_client.messages.*`
  - `project_client.agents.runs.*` → `agents_client.runs.*`
  - `project_client.agents.delete_agent` → `agents_client.delete_agent`
- [ ] **Fix auto function calling**: Move `enable_auto_function_calls()` to `agents_client`
- [ ] **Update message retrieval**: Replace `get_last_message_by_role()` with iteration
- [ ] **Keep AIProjectClient**: Retain for connection management (e.g., `project_client.connections.get()`)
- [ ] **Test syntax**: Run `python -m py_compile your_file.py`
- [ ] **Test execution**: Run the agent end-to-end if dependencies are available

---

## Common Errors & Solutions

### Error 1: AttributeError: 'AgentsOperations' object has no attribute 'create_agent'

**Cause:** Using old pattern `project_client.agents.create_agent()`

**Solution:**

```python
# ❌ Wrong
agent = project_client.agents.create_agent(...)

# ✅ Correct
agents_client = AgentsClient(endpoint, credential)
agent = agents_client.create_agent(...)
```

---

### Error 2: AttributeError: 'ItemPaged' object has no attribute 'get_last_message_by_role'

**Cause:** Method removed in new API version

**Solution:**

```python
# ❌ Wrong
msg = agents_client.messages.get_last_message_by_role(thread_id, role)

# ✅ Correct
from azure.ai.agents.models import ListSortOrder
messages = agents_client.messages.list(thread_id=thread_id, order=ListSortOrder.DESCENDING)
for message in messages:
    if message.role == MessageRole.AGENT:
        # Process message
        break
```

---

### Error 3: UnicodeEncodeError on Windows with emoji output

**Cause:** Windows console doesn't default to UTF-8 encoding

**Solution:**

```python
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

### Error 4: enable_auto_function_calls not found

**Cause:** Calling on wrong object or old API pattern

**Solution:**

```python
# ❌ Wrong
project_client.agents.enable_auto_function_calls(toolset)

# ✅ Correct
agents_client.enable_auto_function_calls(toolset)
```

---

## Automated Migration Script

You can use PowerShell to automate the basic find/replace operations:

```powershell
# Backup first!
Copy-Item agents-*.py -Destination backup/

# Replace project_client.agents. with agents_client.
Get-ChildItem agents-*.py | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace 'project_client\.agents\.','agents_client.' |
    Set-Content $_.FullName
}
```

**Note:** You'll still need to manually:

1. Add imports for `AgentsClient`
2. Add UTF-8 encoding wrapper
3. Create `AgentsClient` instance
4. Update context manager
5. Fix message retrieval patterns
6. Test thoroughly

---

## Example: Complete Before/After

### Before (Old API)

```python
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import MessageRole

def main():
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    with project_client:
        agents_client = project_client.agents

        agent = agents_client.create_agent(
            model=model,
            name="my-agent",
            instructions="You are a helpful assistant"
        )

        thread = agents_client.threads.create()
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello!"
        )

        run = agents_client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )

        response = agents_client.messages.get_last_message_by_role(
            thread_id=thread.id,
            role=MessageRole.AGENT
        )

        if response:
            print(response.text_messages[0].text.value)

        agents_client.delete_agent(agent.id)

if __name__ == '__main__':
    main()
```

### After (New API)

```python
import os
import io
import sys
from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import MessageRole, ListSortOrder

# Configure UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    agents_client = AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    with agents_client:
        agent = agents_client.create_agent(
            model=model,
            name="my-agent",
            instructions="You are a helpful assistant"
        )

        thread = agents_client.threads.create()
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello!"
        )

        run = agents_client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )

        messages = agents_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.DESCENDING
        )

        for msg in messages:
            if msg.role == MessageRole.AGENT:
                for text_msg in msg.text_messages:
                    print(text_msg.text.value)
                break

        agents_client.delete_agent(agent.id)

if __name__ == '__main__':
    main()
```

---

## Tool-Specific Patterns

### Function Calling with ToolSet

```python
from azure.ai.agents.models import FunctionTool, ToolSet

functions = FunctionTool([my_function_1, my_function_2])
toolset = ToolSet()
toolset.add(functions)

with agents_client:
    agents_client.enable_auto_function_calls(toolset)  # Important!
    agent = agents_client.create_agent(
        model=model,
        name="function-agent",
        instructions="Use functions to help users",
        toolset=toolset
    )
```

### Azure AI Search Tool

```python
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType

# AIProjectClient still needed for connections
conn_id = project_client.connections.get(connection_name).id

ai_search = AzureAISearchTool(
    index_connection_id=conn_id,
    index_name=index_name,
    query_type=AzureAISearchQueryType.SIMPLE,
    top_k=3
)

with agents_client:
    agent = agents_client.create_agent(
        model=model,
        name="search-agent",
        instructions="Use Azure AI Search to answer questions",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources
    )
```

### MCP (Model Context Protocol) Tool

```python
from azure.ai.agents.models import McpTool

mcp_tool = McpTool(
    server_label="github",
    server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
    allowed_tools=[]
)
mcp_tool.allow_tool("search_azure_rest_api_code")

with agents_client:
    agent = agents_client.create_agent(
        model=model,
        name="mcp-agent",
        instructions="Use MCP tools to assist users",
        tools=mcp_tool.definitions
    )
```

---

## Testing After Migration

1. **Syntax Check**: `python -m py_compile your_agent.py`
2. **Import Check**: `python -c "import your_module"`
3. **Dry Run**: Execute with minimal configuration
4. **Full Test**: Run with all dependencies configured

---

## Additional Resources

- [Azure AI Agents SDK Documentation](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Foundry](https://ai.azure.com)
- [Azure AI Agents Python SDK](https://pypi.org/project/azure-ai-agents/)
- [Migration Issues Tracker](https://github.com/Azure/azure-sdk-for-python/issues)

---

**Last Updated**: November 21, 2025  
**Applies To**: `azure-ai-agents >= 1.2.0b6`, `azure-ai-projects >= 2.0.0b2`
