# Migration Guide: agents-file-search.py

## ⚠️ MIGRATION BLOCKED - No Upgrade Path Available

**Current Status:** This sample **CANNOT be migrated** to the new Microsoft Foundry API at this time.

**Blocker:** The `FileSearchTool` is not available in `azure.ai.projects.models`. The new API currently only supports `MCPTool`.

**Recommendation:** Keep this sample using the legacy `AgentsClient` API until Microsoft adds File Search tool support to the new API.

---

## Current Implementation (Legacy API)

This sample uses:

- **API:** `azure.ai.agents.AgentsClient`
- **Tool:** `FileSearchToolDefinition` with `FileSearchToolResource`
- **Pattern:** Thread/Run with polling
- **Vector Store:** Pre-configured via `VECTOR_STORE_ID` environment variable

```python
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FileSearchToolDefinition, FileSearchToolResource, ToolResources

agent = agents_client.create_agent(
    model=model,
    name="file-search-agent",
    instructions="You are a helpful agent that can search through documents...",
    tools=[FileSearchToolDefinition()],
    tool_resources=ToolResources(
        file_search=FileSearchToolResource(
            vector_store_ids=[vector_store_id]
        )
    )
)
```

---

## Alternative: Foundry IQ (Knowledge Base)

If you need RAG capabilities with the new API, consider using **Foundry IQ** instead. See `agents-foundry-iq.py` for a working example.

### Migration to Foundry IQ

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

project_client = AIProjectClient(endpoint=endpoint, credential=credential)
openai_client = project_client.get_openai_client()

# Get search endpoint from connection
search_conn = project_client.connections.get("procodeaisearch")
search_endpoint = search_conn.properties.get("target")

# Construct MCP endpoint for knowledge base
knowledge_base_name = "my-knowledge-base"
mcp_endpoint = f"{search_endpoint}/knowledgebases/{knowledge_base_name}/mcp?api-version=2025-11-01-preview"

# Create MCP tool for knowledge base
mcp_kb_tool = MCPTool(
    server_label="knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",
    allowed_tools=["knowledge_base_retrieve"],
    project_connection_id="foundry-iq-connection"
)

agent = project_client.agents.create_version(
    agent_name="file-search-agent",
    definition=PromptAgentDefinition(
        model=model,
        instructions="""You are a helpful assistant that must use the knowledge base to answer questions.
        Always provide annotations using the MCP knowledge base tool.""",
        tools=[mcp_kb_tool]
    )
)

# Use streaming responses
response = openai_client.responses.create(
    input="Tell me about Equinox Gold",
    stream=True,
    extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
)

for event in response:
    if event.type == "response.output_text.delta":
        print(event.delta, end='', flush=True)
    elif event.type == "response.completed":
        print()
        break
```

See `foundry-iq-todo.md` and `agents-foundry-iq.py` for complete setup instructions.

---

## Recommended File Header Update

Add this note at the top of the file:

```python
# NOTE: This sample uses the legacy AgentsClient API because FileSearchTool
# is not yet available in the new Microsoft Foundry API (AIProjectClient).
# See agents-file-search-MIGRATION.md for details and alternatives.
```

---

**Last Updated:** November 27, 2025
