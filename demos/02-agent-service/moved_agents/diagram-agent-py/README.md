# Diagram Agent Python Demo

This demo shows how to create an AI agent using Azure AI Agent Service that can analyze data and generate diagrams.

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
uv run python agent.py
```

The agent will upload the data file, analyze it, and can generate charts upon request.
