# Agent Framework to Foundry Migration Status

## Migration Summary

All demos with the `agentfw_` prefix have been successfully migrated from Microsoft Agent Framework to Microsoft Foundry Responses API.

## Migration Details

| File | Status | Notes |
|------|--------|-------|
| `agentfw_openai_chat.py` | ✅ Migrated | Direct chat using Foundry Responses API |
| `agentfw_create_agent.py` | ✅ Migrated | Agent creation with `create_version()` and `PromptAgentDefinition` |
| `agentfw_streaming.py` | ✅ Migrated | Streaming responses using `stream=True` |
| `agentfw_use_existing_agent.py` | ✅ Migrated | Connect to existing agent by name/version |
| `agentfw_threading.py` | ✅ Migrated | Conversation persistence with JSON serialization |
| `agentfw_chat_history.py` | ✅ Migrated | Chat history with reducers (sync version) |
| `agentfw_long_term_memory.py` | ✅ Migrated | AI-powered memory extraction using Foundry |
| `agentfw_middleware.py` | ✅ Migrated | Middleware patterns (timing, security, token counter) |
| `agentfw_observability.py` | ✅ Migrated | OpenTelemetry observability with HTML reports |
| `agentfw_structured_output.py` | ✅ Migrated | Structured output with Pydantic validation |
| `agentfw_multimodal.py` | ✅ Migrated | Multimodal image processing with base64 encoding |

## Key Changes Made

### API Changes

1. **Client Initialization**
   - Before: `AzureOpenAIChatClient` from `agent_framework.azure`
   - After: `AIProjectClient` from `azure.ai.projects` + `get_openai_client()`

2. **Agent Creation**
   - Before: `client.create_agent(model, name, instructions)`
   - After: `project_client.agents.create_version(agent_name, definition=PromptAgentDefinition(...))`

3. **Conversation Model**
   - Before: Threads and `run_stream()` on agent
   - After: Direct `openai_client.responses.create()` with conversation history

4. **Agent Reference**
   - Before: By agent ID
   - After: By name + version in `extra_body`

5. **Cleanup**
   - Before: `delete_agent(agent.id)`
   - After: `project_client.agents.delete_version(agent_name, agent_version)`

### Utility Updates

- `utils/chat_history.py`: Added `SummarizingChatReducerFoundry` class for sync Foundry API support
- Added sync versions of methods (`add_message_sync`, `get_messages_sync`, `reduce_sync`)

## Environment Variables

The demos now use these environment variables:
- `AZURE_AI_PROJECT_ENDPOINT`: Azure AI Foundry project endpoint
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: Model deployment name (default: gpt-4o)
- `DELETE`: Whether to delete agent versions after demo (default: true)

## Migration Date

2024-11-26

## References

- [Migration Guide](https://learn.microsoft.com/en-gb/azure/ai-foundry/agents/how-to/migrate?view=foundry)
- [Responses API Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry-classic)
- [Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
