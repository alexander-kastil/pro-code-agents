# Microsoft Foundry Agents - Basics & Concepts

> **Note**: These demos have been migrated from Microsoft Agent Framework to Microsoft Foundry Responses API.
> See `agentfw-migration-status.md` for migration details.

- Introduction to Azure AI Foundry Agents
- Chat Clients vs Agents: Key differences
- Agent types and configuration essentials
- Working with versioned agents using Foundry Responses API
- Conversation persistence and history management
- Managing agent memory
- Middleware patterns & Observability
- Multi-modal capabilities and structured outputs

## Demo Files

| Filename                        | Description                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| `agentfw_openai_chat.py`        | Direct Azure AI Foundry chat using Responses API                                     |
| `agentfw_create_agent.py`       | Create a new Azure AI Foundry Agent and chat with it interactively                   |
| `agentfw_streaming.py`          | Demonstrate response streaming for real-time token-by-token output                   |
| `agentfw_use_existing_agent.py` | Connect to an existing Azure AI Foundry Agent by name/version                        |
| `agentfw_threading.py`          | Conversation serialization and deserialization with automatic save/restore           |
| `agentfw_chat_history.py`       | Chat history management with reducers and JSON serialization/deserialization         |
| `agentfw_long_term_memory.py`   | AI-powered long-term memory with intelligent context extraction                      |
| `agentfw_middleware.py`         | Complete middleware demo with timing, security, function logging, and token counting |
| `agentfw_observability.py`      | OpenTelemetry observability with comprehensive span data collection                  |
| `agentfw_structured_output.py`  | Extract structured data using Pydantic models                                        |
| `agentfw_multimodal.py`         | Process images with vision capabilities and extract structured invoice data          |

## Environment Variables

Set these in your `.env` file (see `.env.copy` for template):

```bash
# Azure AI Foundry project endpoint
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project

# Model deployment name
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# Whether to delete agent versions after demo (default: true)
DELETE=true
```
