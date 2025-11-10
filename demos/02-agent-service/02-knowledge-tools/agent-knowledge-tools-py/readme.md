# Diagram Agent Python Demo

This demo shows how to create an AI agent using Azure AI Agent Service that can analyze data and generate diagrams.

Samples:

- `agent-basics.py`: Main script to create and run the agent.
- `agent-event-handler.py`: Custom event handler for processing agent events.
- `agent-response-format.py`: Defines the response format for the agent.
- `agent-input-url.py`: Handles URL input for the agent.
- `agent-input-file.py`: Handles file input for the agent.
- `agent-input-base64.py`: Handles base64 encoded input for the agent.

## Prerequisites

- Python 3.8+
- Azure AI Foundry project
- uv package manager

## Installation

1. Install dependencies using uv:

```bash
uv sync
```

2. Copy `.env.copy` to `.env` and fill in your Azure AI project connection string and model deployment name.

## Running the Agent

```bash
uv run python agent-basics.py
```

The agent will upload the data file, analyze it, and can generate charts upon request.
