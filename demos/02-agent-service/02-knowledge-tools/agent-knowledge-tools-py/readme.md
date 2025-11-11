# Diagram Agent Python Demo

This demo shows how to create an AI agent using Azure AI Agent Service that can analyze data and generate diagrams.

Samples:

| File                         | Description                                                                       |
| ---------------------------- | --------------------------------------------------------------------------------- |
| `agent-file-search.py`       | File search to find and analyze files.                                            |
| `agents-ai-search-rag.py`    | Azure AI Search for retrieval augmented generation (RAG).                         |
| `agents-function-calling.py` | Function calling tool pattern                                                     |
| `agents-code-interpreter.py` | Tools: Code interpreter                                                           |
| `agent-input-file.py`        | Handles file input for the agent. Analyzes an image                               |
| `agent-input-base64.py`      | Handles base64 encoded input for the agent. Analyzes an image                     |
| `agent-output.py`            | Takes an input, encodes it in a QR code and stores it in an Azure Storage account |

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
