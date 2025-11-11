# Connected Agents Python Demo

This demo demonstrates a multi-agent ticket triage system where a main orchestrator agent delegates specialized tasks to three connected sub-agents. The Priority Agent assesses ticket urgency, the Team Agent determines ownership, and the Effort Agent estimates required work. Each connected agent operates independently with its own instructions, while the main agent coordinates their outputs to provide comprehensive ticket analysis.

## What This Demo Shows

This example demonstrates the **ConnectedAgentTool** pattern in Azure AI Agent Service. Each specialized agent is wrapped as a `ConnectedAgentTool` and added to the main orchestrator agent's toolset. When the orchestrator receives a user query, it automatically delegates to the appropriate connected agents based on their descriptions, enabling multi-agent collaboration without manual routing logic. The demo showcases agent creation, tool registration, thread management, and proper cleanup of all agent resources.

## How to Run

1. Copy `.env.copy` to `.env` and configure your Azure AI project endpoint and model deployment
2. Install dependencies: `uv sync` (or `pip install -r requirements.txt`)
3. Run the agent: `uv run python agent_triage.py` (or `python agent_triage.py`)
4. Optional: Set `VERBOSE_OUTPUT=true` for detailed logging
5. Optional: Set `CREATE_MERMAID_DIAGRAM=true` to generate Mermaid sequence diagrams of agent interactions
6. Optional: Set `AZURE_HTTP_LOG=true` to enable detailed HTTP-level visualization (requires `CREATE_MERMAID_DIAGRAM=true`)

## Multi-Level Mermaid Diagram Generation

When `CREATE_MERMAID_DIAGRAM=true` is set, the system generates **a single comprehensive Mermaid diagram file** for each run, with multiple sections providing different levels of detail:

### 1. Default Level - Agent Interaction Diagram
- Shows the basic agent interactions and message flows
- Focuses on user-facing communication patterns  
- Best for understanding the high-level workflow
- Sequence diagram format showing message exchanges

### 2. Verbose Level - System Setup Flowchart
- Includes agent creation and tool registration details
- Shows the complete setup and execution flow
- Best for debugging and understanding internal processes
- Flowchart format showing system initialization

### 3. HTTP Level - API Communication Layer ✨ **NEW & IMPROVED**
- **Detailed HTTP request/response visualization** with enhanced features:
  - 📤 Sequential numbering for each API call (e.g., [1], [2], [3])
  - 📝 Operation descriptions (e.g., "Create agent", "Start run", "List messages")
  - ✓ Status code indicators (✓ = success, ⚠ = client error, ✗ = server error)
  - 🔗 Normalized endpoint paths with {id} placeholders
  - 📊 HTTP events timeline table showing all requests chronologically
- Captures complete HTTP communication between client and Azure AI Agent Service
- Shows API-level patterns including agent creation, threading, messaging, and cleanup
- Best for understanding the network communication layer and API usage

The diagram is generated using **Jinja2 templates** located in the `templates/` directory, making it easy to customize for your specific needs.

### Environment Variables for Logging

- `VERBOSE_OUTPUT=true` - Enable detailed console logging
- `AZURE_HTTP_LOG=true` - Enable Azure SDK HTTP-level logging (captured in HTTP diagram section)
- `CREATE_MERMAID_DIAGRAM=true` - Generate comprehensive Mermaid diagram file
- `MERMAID_DIR=diagrams` - Directory to save diagram files (default: `diagrams`)

### Demo Script

To see the HTTP visualization improvements without needing Azure credentials, run:

```bash
python demo_http_visualization.py
```

This demo script simulates a complete agent triage workflow and shows:
- The generated HTTP sequence diagram with all improvements
- HTTP events summary with 13+ API calls
- Saved diagram file in the `demo_diagrams/` directory

### Running Tests

To verify the HTTP visualization functionality:

```bash
python -m unittest test_http_visualization -v
```

All 9 tests should pass, covering:
- Endpoint normalization
- Operation descriptions
- Pattern matching
- Status emoji indicators
- HTTP event capturing
- Complete workflow integration
