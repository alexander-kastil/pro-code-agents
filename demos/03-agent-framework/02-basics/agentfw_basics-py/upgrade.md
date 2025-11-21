# Azure AI Agents SDK Migration Guide

## Overview

This guide documents the migration from `azure-ai-projects` (`AIProjectClient.agents`) to `azure-ai-agents` (`AgentsClient`) API patterns for Azure AI Agent applications.

**Affected SDK Versions:**

- **Old (Deprecated)**: `azure-ai-projects <= 2.0.0b1`
- **New (Required)**: `azure-ai-agents >= 1.2.0b6`, `azure-ai-projects >= 2.0.0b2`

---

## Breaking Changes Summary

### 1. Client Instantiation Pattern

#### Old (Deprecated)

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

#### New (Required)

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

#### Old

```python
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, FunctionTool, ToolSet
```

#### New

```python
from azure.ai.agents import AgentsClient
from azure.ai.projects import AIProjectClient  # Only for connections
from azure.ai.agents.models import MessageRole, FunctionTool, ToolSet
```

---

### 3. Agent Operations

All agent operations now go directly through `AgentsClient` instead of `project_client.agents.*`

#### Old

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

#### New

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

#### Old (Incorrect - caused AttributeError)

```python
with project_client:
    project_client.agents.enable_auto_function_calls(toolset)
    agent = project_client.agents.create_agent(...)
```

#### New (Correct)

```python
with agents_client:
    agents_client.enable_auto_function_calls(toolset)
    agent = agents_client.create_agent(...)
```

**Note:** `enable_auto_function_calls()` is called on `AgentsClient`, not on `AgentsOperations`.

---

### 5. Message Retrieval (Deprecated Method)

#### Old (No longer available)

```python
response_message = agents_client.messages.get_last_message_by_role(
    thread_id=thread.id,
    role=MessageRole.AGENT
)
if response_message:
    for text_message in response_message.text_messages:
        print(text_message.text.value)
```

#### New (Manual iteration)

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
