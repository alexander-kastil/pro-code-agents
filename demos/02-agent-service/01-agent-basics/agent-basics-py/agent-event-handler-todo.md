# agent-event-handler.py Migration TODO

## Status

Migration completed but **BLOCKED** by authentication issue.

## Issue

Getting authentication error when calling `openai_client.responses.create()`:

```
openai.AuthenticationError: Error code: 401 - {'statusCode': 401, 'message': 'Unauthorized. Access token is missing, invalid, audience is incorrect (https://ai.azure.com), or have expired.'}
```

## Root Cause

This is **NOT** a migration issue. The same error occurs with the previously migrated `agent-input-file.py`. This indicates:

- Azure credentials have expired or need to be refreshed
- Possible authentication configuration issue with the Azure AI Foundry project
- The `DefaultAzureCredential()` may need to be re-authenticated

## Migration Changes Made

- ✅ Updated imports from `azure.ai.agents` to `azure.ai.projects`
- ✅ Changed client from `AgentsClient` to `AIProjectClient`
- ✅ Updated agent creation to use `create_version()` with `PromptAgentDefinition`
- ✅ Replaced thread/run flow with responses API
- ✅ Added DELETE-based cleanup logic
- ✅ Added try/except error handling
- ⚠️ **Streaming functionality needs testing** - Changed from custom `AgentEventHandler` to responses API (streaming capability to be validated once auth is fixed)

## Testing Status

- ✅ Agent creation works
- ❌ Response creation fails due to auth issue
- ⏸️ Streaming not tested yet
- ⏸️ Cleanup not tested yet

## Next Steps

1. **Fix authentication issue first** (affects all agents using responses API)
   - Check Azure credentials: `az login` or refresh credentials
   - Verify project endpoint is correct
   - Ensure DefaultAzureCredential has proper permissions
2. **After auth is fixed:**
   - Test non-streaming response flow
   - Implement and test streaming functionality
   - Verify streaming events match original behavior
   - Test cleanup with DELETE=true

## Notes on Streaming Migration

The old API used:

```python
class MyEventHandler(AgentEventHandler[str]):
    def on_message_delta(self, delta: "MessageDeltaChunk") -> Optional[str]:
        # Custom event handling
    # Other event methods...

with agents_client.runs.stream(thread_id, agent_id, event_handler=MyEventHandler()) as stream:
    for event_type, event_data, func_return in stream:
        # Process events
```

The new API should use:

```python
stream = openai_client.responses.create(..., stream=True)
for chunk in stream:
    # Process streaming chunks
```

Need to verify that the new streaming API provides equivalent functionality for event handling.
