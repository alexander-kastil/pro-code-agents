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

## How it works

The triage agent uses three connected agents:
- **Priority Agent**: Assesses the urgency of tickets
- **Team Agent**: Determines which team should handle the ticket
- **Effort Agent**: Estimates the work required to complete the ticket

The main agent orchestrates these connected agents to provide a comprehensive ticket triage.
