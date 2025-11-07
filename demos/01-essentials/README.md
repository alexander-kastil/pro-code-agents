# Python Environment Setup for demos/01-essentials

## Overview

All Python scripts in the `demos/01-essentials` directory and its subdirectories use a shared Python virtual environment located at the root of the repository (`/workspace/.venv` in the devcontainer).

## Automatic Setup

When the devcontainer starts, the `post-create.sh` script automatically:

1. Creates a Python virtual environment at `/workspace/.venv`
2. Installs all required packages from `requirements.txt`
3. Sets proper ownership for the virtual environment

## Using the Virtual Environment

### Activating the Environment

To activate the virtual environment in your terminal:

```bash
source /workspace/.venv/bin/activate
```

### Running Python Scripts

Once activated, you can run any Python script in `demos/01-essentials`:

```bash
# Example: Run a script from the AI Foundry SDK demos
cd demos/01-essentials/01-ai-foundry/02-sdk/foundry-sdk-py
python chat-foundry.py
```

### Installed Packages

The following packages are installed in the shared environment:

- **Azure AI**: `azure-ai-projects`, `azure-ai-inference`, `azure-ai-evaluation`
- **Azure Core**: `azure-identity`, `azure-core`, `azure-search-documents`
- **OpenTelemetry**: `opentelemetry-api`, `azure-monitor-opentelemetry`
- **AI/ML Libraries**: `openai`, `pandas`, `langchain-community`, `fastmcp`
- **Utilities**: `python-dotenv`, `agent-framework`, `ipykernel`

## Manual Installation

If you need to manually reinstall packages:

```bash
cd /workspace
source .venv/bin/activate
pip install -r requirements.txt
```

## Adding New Dependencies

To add new Python dependencies:

1. Add the package name to `/workspace/requirements.txt`
2. Install it in the virtual environment:
   ```bash
   source /workspace/.venv/bin/activate
   pip install <package-name>
   ```
3. Commit the updated `requirements.txt` file

## Directory Structure

```
demos/01-essentials/
├── 01-ai-foundry/
│   ├── 02-sdk/
│   │   ├── foundry-sdk-py/       # AI Foundry SDK demos
│   │   └── function-calling-py/  # Function calling examples
│   ├── 05-rag/
│   │   └── rag-azure/           # RAG with Azure AI Search
│   └── 06-evaluations/
│       └── evaluations-py/      # Evaluation examples
└── 03-mcp/
    └── youtube-transcriber-mcp-py/  # MCP server example
```

All scripts in these directories use the shared virtual environment at `/workspace/.venv`.
