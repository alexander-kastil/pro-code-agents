# Connected Agents Python Demo

This demo demonstrates a multi-agent ticket triage system where a main orchestrator agent delegates specialized tasks to three connected sub-agents. The Priority Agent assesses ticket urgency, the Team Agent determines ownership, and the Effort Agent estimates required work. Each connected agent operates independently with its own instructions, while the main agent coordinates their outputs to provide comprehensive ticket analysis.

## What This Demo Shows

This example demonstrates the **ConnectedAgentTool** pattern in Azure AI Agent Service. Each specialized agent is wrapped as a `ConnectedAgentTool` and added to the main orchestrator agent's toolset. When the orchestrator receives a user query, it automatically delegates to the appropriate connected agents based on their descriptions, enabling multi-agent collaboration without manual routing logic. The demo showcases agent creation, tool registration, thread management, and proper cleanup of all agent resources.

## How to Run

1. Copy `.env.copy` to `.env` and configure your Azure AI project endpoint and model deployment
2. Install dependencies: `uv sync` (or `pip install -r requirements.txt`)
3. Run the agent: `uv run python agent_triage.py` (or `python agent_triage.py`)
4. Optional: Set `VERBOSE_OUTPUT=true` for detailed logging
5. Optional: Set `CREATE_MERMAID_DIAGRAM=true` to generate Mermaid sequence diagrams of agent interactions (see [MERMAID_DIAGRAMS.md](MERMAID_DIAGRAMS.md))

## Multi-Level Mermaid Diagram Generation

When `CREATE_MERMAID_DIAGRAM=true` is set, the system generates **three separate Mermaid diagram files** for each run, providing different levels of detail:

### 1. Default Diagram (`*_default.md`)
- Shows the basic agent interactions and message flows
- Focuses on user-facing communication patterns
- Best for understanding the high-level workflow

### 2. Verbose Diagram (`*_verbose.md`)
- Includes all events from the default diagram
- Adds agent creation and tool registration details
- Contains a detailed event log with timestamps
- Best for debugging and understanding internal processes

### 3. HTTP Diagram (`*_http.md`)
- Focuses on API-level communication patterns
- Captures HTTP requests and responses between components
- Lists HTTP events with timestamps and details
- Best for understanding the network communication layer

All three diagrams are generated using **Jinja2 templates** located in the `templates/` directory, making them easy to customize for your specific needs.

### Environment Variables for Logging

- `VERBOSE_OUTPUT=true` - Enable detailed console logging
- `AZURE_HTTP_LOG=true` - Enable Azure SDK HTTP-level logging (captured in HTTP diagram)
- `CREATE_MERMAID_DIAGRAM=true` - Generate all three Mermaid diagram files
- `MERMAID_DIR=diagrams` - Directory to save diagram files (default: `diagrams`)
