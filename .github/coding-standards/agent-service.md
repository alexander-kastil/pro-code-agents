# Azure AI Foundry Agent Service Coding Standards

## Overview

This document provides coding standards for building agents using the Azure AI Foundry Agent Service. The Agent Service provides pre-built capabilities for creating AI agents with tools, knowledge bases, and file handling.

## Python Standards

### Client Initialization

Use the `AIProjectClient` to interact with the Agent Service:

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load environment variables
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")

# Create client
agents_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)
```

### Agent Creation

#### Basic Agent

```python
# Create a basic agent
agent = agents_client.agents.create_agent(
    model=model,
    name="basic-agent",
    instructions="You are a helpful agent"
)

print(f"Created agent: {agent.name}, ID: {agent.id}")
```

#### Agent with Tools

```python
from azure.ai.agents.models import FunctionTool, ToolSet

# Define a function tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"The weather in {location} is sunny."

# Create function tool definition
functions = FunctionTool(functions=[get_weather])

# Create agent with tools
agent = agents_client.agents.create_agent(
    model=model,
    name="weather-agent",
    instructions="You are a weather assistant. Use the get_weather function to answer questions.",
    tools=functions.definitions
)
```

#### Agent with File Search

```python
from azure.ai.agents.models import FileSearchTool

# Create agent with file search capability
agent = agents_client.agents.create_agent(
    model=model,
    name="document-agent",
    instructions="You are a document analyst. Use file search to answer questions.",
    tools=[{"type": "file_search"}]
)
```

### Thread Management

```python
# Create a thread for conversation
thread = agents_client.agents.threads.create()
print(f"Created thread, thread ID: {thread.id}")

# Add a message to the thread
message = agents_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hello, tell me a joke"
)
```

### Running Agents

#### Basic Run

```python
# Create a run
run = agents_client.agents.runs.create(
    thread_id=thread.id,
    agent_id=agent.id
)

# Wait for completion
while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = agents_client.agents.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

# Get messages
messages = agents_client.agents.messages.list(thread_id=thread.id)
for message in messages:
    print(f"{message.role}: {message.content[0].text.value}")
```

#### Run with Event Handler

```python
from azure.ai.agents.models import RunStatus

class EventHandler:
    def __init__(self, agents_client, thread_id, run_id):
        self.client = agents_client
        self.thread_id = thread_id
        self.run_id = run_id

    def on_message_delta(self, delta):
        """Handle streaming message deltas."""
        if delta.content:
            for content in delta.content:
                if hasattr(content, 'text') and content.text:
                    print(content.text.value, end='', flush=True)

    def on_run_step_created(self, step):
        """Handle new run step creation."""
        print(f"\n[Step Created: {step.type}]")

    def on_run_completed(self, run):
        """Handle run completion."""
        print("\n[Run Completed]")

# Use event handler
handler = EventHandler(agents_client, thread.id, run.id)

# Create run with streaming
run = agents_client.agents.runs.create_and_stream(
    thread_id=thread.id,
    agent_id=agent.id,
    event_handler=handler
)
```

### Function Calling

```python
from azure.ai.agents.models import SubmitToolOutputsAction

# Handle function calls during run
while run.status == "requires_action":
    if run.required_action.type == "submit_tool_outputs":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            if tool_call.function.name == "get_weather":
                # Parse arguments
                import json
                args = json.loads(tool_call.function.arguments)

                # Call the function
                result = get_weather(args["location"])

                # Add output
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": result
                })

        # Submit outputs
        run = agents_client.agents.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    # Wait and check again
    time.sleep(1)
    run = agents_client.agents.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
```

### File Handling

#### Upload Files

```python
# Upload a file for the agent
with open("document.pdf", "rb") as f:
    file = agents_client.agents.files.upload(
        file=f,
        purpose="assistants"
    )

print(f"Uploaded file: {file.id}")
```

#### Attach Files to Messages

```python
# Create message with file attachment
message = agents_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze this document",
    file_ids=[file.id]
)
```

#### Download Agent Outputs

```python
# Download files created by the agent
output_file_id = "file-abc123"
file_content = agents_client.agents.files.download(file_id=output_file_id)

with open("output.png", "wb") as f:
    f.write(file_content)
```

### Knowledge Bases (Vector Stores)

```python
# Create a vector store
vector_store = agents_client.agents.vector_stores.create(
    name="my-knowledge-base"
)

# Upload files to vector store
with open("document.pdf", "rb") as f:
    file = agents_client.agents.files.upload(
        file=f,
        purpose="assistants"
    )

# Add file to vector store
agents_client.agents.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file.id
)

# Create agent with vector store
agent = agents_client.agents.create_agent(
    model=model,
    name="knowledge-agent",
    instructions="You are a helpful assistant. Use the knowledge base to answer questions.",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id]
        }
    }
)
```

### Connected Agents (Multi-Agent Systems)

```python
# Create a triage agent
triage_agent = agents_client.agents.create_agent(
    model=model,
    name="triage-agent",
    instructions="""You are a triage agent.
    Analyze user requests and determine which specialist agent should handle them.
    Route to:
    - weather-agent for weather queries
    - document-agent for document analysis
    """
)

# Create specialist agents
weather_agent = agents_client.agents.create_agent(
    model=model,
    name="weather-agent",
    instructions="You are a weather specialist."
)

document_agent = agents_client.agents.create_agent(
    model=model,
    name="document-agent",
    instructions="You are a document analysis specialist."
)

# Implement routing logic
def route_to_agent(user_query: str):
    # Ask triage agent
    thread = agents_client.agents.threads.create()
    message = agents_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Which agent should handle this: {user_query}"
    )

    run = agents_client.agents.runs.create(
        thread_id=thread.id,
        agent_id=triage_agent.id
    )

    # Wait for response
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = agents_client.agents.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    # Get triage decision
    messages = agents_client.agents.messages.list(thread_id=thread.id)
    decision = messages.data[0].content[0].text.value

    # Route to appropriate agent
    if "weather" in decision.lower():
        return weather_agent.id
    elif "document" in decision.lower():
        return document_agent.id
    else:
        return triage_agent.id
```

### Observability and Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log agent operations
logger.info(f"Creating agent: {agent.name}")
logger.info(f"Agent created with ID: {agent.id}")
logger.info(f"Starting run on thread: {thread.id}")

# Log run steps
run_steps = agents_client.agents.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
)

for step in run_steps:
    logger.info(f"Step {step.id}: {step.type} - {step.status}")
```

## Best Practices

### Agent Design

1. **Clear Instructions**: Write detailed, specific instructions for your agents
2. **Tool Selection**: Only include tools that the agent needs
3. **Context Management**: Keep conversation threads focused and manageable
4. **Error Handling**: Always check run status and handle failures gracefully

### Performance

1. **Async Operations**: Use async clients for better performance in production
2. **Thread Reuse**: Reuse threads for ongoing conversations
3. **Cleanup**: Delete agents and threads when no longer needed

```python
# Cleanup
agents_client.agents.delete_agent(agent_id=agent.id)
agents_client.agents.threads.delete(thread_id=thread.id)
```

### Monitoring

1. **Track Usage**: Monitor token usage and API calls
2. **Log Failures**: Log all failed runs for debugging
3. **Trace Conversations**: Keep conversation history for analysis

### Security

1. **Input Validation**: Validate user inputs before sending to agents
2. **Content Filtering**: Use Azure AI Content Safety for filtering
3. **Access Control**: Implement proper authentication and authorization
4. **Data Privacy**: Handle sensitive data according to compliance requirements

## Versioning & SDK Conventions (Agent Service)

To ensure reproducible training environments and reduce breaking changes, we pin specific preview/GA SDK versions and follow updated API usage patterns.

### Pinned SDK Versions

| Component      | Package           | Version | Rationale                                               |
| -------------- | ----------------- | ------- | ------------------------------------------------------- |
| Project Client | azure-ai-projects | 2.0.0b1 | Adopt preview features while standardizing across demos |
| Agents Service | azure-ai-agents   | 1.2.0b6 | Required for BrowserAutomationTool & ComputerUseTool    |
| Identity       | azure-identity    | 1.16.0  | Stable credential flow for training labs                |

All requirements are pinned with `==` (no ranges) in each demo `requirements.txt` to avoid inadvertent API drift.

### Environment Variables

Required variables (must exist in `.env`):

- `PROJECT_ENDPOINT` – Azure AI Foundry Project endpoint (not connection string)
- `MODEL_DEPLOYMENT_NAME` – Model deployment name (e.g. `gpt-4o-mini`) used by `create_agent` (legacy `MODEL_DEPLOYMENT` still accepted for backward compatibility)
- Optional: `AUTO_TEST_PROMPT` – Enables non-interactive smoke testing of agent scripts.

### Updated API Usage (2.x project client + 1.2.x agents)

Use the nested resource groups under `project_client.agents`:

Correct patterns:

```python
thread = project_client.agents.threads.create()
project_client.agents.messages.create(thread_id=thread.id, role="user", content="Hello")
run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
messages = project_client.agents.messages.list(thread_id=thread.id)
last = messages.get_last_text_message_by_role("assistant")
```

Deprecated / incorrect (do NOT use):

```python
# project_client.agents.create_message(...)  # OLD pattern
# project_client.agents.list_messages(...)   # OLD pattern
```

### Common Pitfalls & Fixes

| Pitfall                     | Symptom                                                                   | Fix                                                                                            |
| --------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Using old message APIs      | `AttributeError: 'AgentsClient' object has no attribute 'create_message'` | Replace with `project_client.agents.messages.create`                                           |
| Unpinned dependencies       | Random AttributeErrors after `pip install -U`                             | Pin versions with `==` as listed above                                                         |
| Missing endpoint var        | `KeyError: 'PROJECT_ENDPOINT'` or auth failure                            | Ensure `.env` has `PROJECT_ENDPOINT` and loaded via `dotenv`                                   |
| Function tool not executing | No tool call despite definitions                                          | Call `enable_auto_function_calls(toolset)` before `create_agent` (when auto execution desired) |

### Migration Notes (1.0.0 -> 2.0.0b1)

1. Retain `AIProjectClient` construction; endpoint & credential parameters unchanged.
2. Message and thread operations remain under `project_client.agents.messages` / `threads` groups.
3. Replace any helper wrappers referencing removed convenience methods with explicit nested resource calls.
4. Re-test function calling flows (auto vs manual) after upgrade—ensure toolset passed into `create_agent` when relying on auto execution.

### Smoke Test Convention

Each agent demo may define `AUTO_TEST_PROMPT` to allow headless CI verification:

```powershell
$env:AUTO_TEST_PROMPT = 'Smoke test prompt'; python .\agents-function-calling.py
```

Scripts should branch on presence of this variable to avoid interactive waits.

### Documentation Updates

Whenever SDK version changes, update:

1. `requirements.txt`
2. This Versioning & SDK Conventions section (table + migration notes)
3. Any code snippets showing deprecated calls.

---

## Educational Focus

When creating demos and examples:

- Focus on one concept at a time
- Provide clear comments explaining what each section does
- Show both simple and advanced patterns
- Include error handling examples
- Demonstrate cleanup operations
