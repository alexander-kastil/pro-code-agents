# Connected Agents Python Demo

This demo demonstrates a multi-agent ticket triage system where a main orchestrator agent delegates specialized tasks to three connected sub-agents. The Priority Agent assesses ticket urgency, the Team Agent determines ownership, and the Effort Agent estimates required work. Each connected agent operates independently with its own instructions, while the main agent coordinates their outputs to provide comprehensive ticket analysis.

## How to Run

1. Copy `.env.copy` to `.env` and configure your Azure AI project endpoint and model deployment
2. Install dependencies: `uv sync` (or `pip install -r requirements.txt`)
3. Run the agent: `uv run python agent_triage.py` (or `python agent_triage.py`)
4. Optional: Set `VERBOSE_OUTPUT=true` for detailed logging

## What This Demo Shows

This example demonstrates the **ConnectedAgentTool** pattern in Azure AI Agent Service. Each specialized agent is wrapped as a `ConnectedAgentTool` and added to the main orchestrator agent's toolset. When the orchestrator receives a user query, it automatically delegates to the appropriate connected agents based on their descriptions, enabling multi-agent collaboration without manual routing logic. The demo showcases agent creation, tool registration, thread management, and proper cleanup of all agent resources.

## Prerequisites

- Python 3.8+
- Azure AI Foundry project
- uv package manager (optional, but recommended)

## Installation

### Using uv (recommended)

1. Install dependencies using uv:

```bash
uv sync
```

2. Copy `.env.copy` to `.env` and fill in your Azure AI project endpoint and model deployment name.

### Using pip

1. Install dependencies using pip:

```bash
pip install -r requirements.txt
```

2. Copy `.env.copy` to `.env` and fill in your Azure AI project endpoint and model deployment name.

## Running the Agent

### Using uv

```bash
uv run python agent_triage.py
```

### Using pip

```bash
python agent_triage.py
```

### Verbose / Debug Output

Set `VERBOSE_OUTPUT` to enable extra debug logging (tool definitions, raw run objects, full message objects). Only the exact string `true` (lowercase) enables verbose mode. Example (PowerShell):

```powershell
$env:VERBOSE_OUTPUT=true; python agent_triage.py
```

You can also set it in your `.env` file:

```properties
VERBOSE_OUTPUT=true
```

When `VERBOSE_OUTPUT` is not `true`, only application INFO logs are shown. Azure SDK HTTP request/response logs are suppressed by default.

Colors:

- INFO logs are yellow
- DEBUG (verbose) logs are white

To show Azure SDK HTTP logs without full verbose mode, set:

```properties
AZURE_HTTP_LOG=true
```

## How it works

The triage agent uses three connected agents:

- **Priority Agent**: Assesses the urgency of tickets
- **Team Agent**: Determines which team should handle the ticket
- **Effort Agent**: Estimates the work required to complete the ticket

The main agent orchestrates these connected agents to provide a comprehensive ticket triage.

### Output Details

The script now logs key lifecycle events:

- Environment / configuration detection
- Creation of each connected agent and the triage agent (IDs shown)
- Thread creation and message sending
- Run status and message stream (each message role + content)
- Cleanup of all agents

Errors during run are surfaced with `ERROR` log level; missing env vars trigger a `WARNING`.
