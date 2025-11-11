# Connected Agents Python Demo

This demo shows how to create a multi-agent solution using Azure AI Agent Service with connected agents for ticket triage.

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

When `VERBOSE_OUTPUT` is not `true`, the script doesn't emit any logs. The console may still clear at startup for a clean screen.

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
