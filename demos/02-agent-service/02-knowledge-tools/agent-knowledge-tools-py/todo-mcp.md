# TODO: agents-mcp.py

## Issue

The MCP agent requires a model that supports MCP (Model Context Protocol) tools.

**Error Message:**

```
The model 'gpt-5-mini' cannot be used with the following tools: mcp.
This model only supports Responses API compatible tools.
```

## Fixed Issues

✅ Removed invalid import `RunStepActivityDetails` that was causing ImportError

## Required Actions

### 1. Update Model Deployment

Change the `MODEL_DEPLOYMENT` variable in your `.env` file:

```
MODEL_DEPLOYMENT="gpt-4o"
```

or

```
MODEL_DEPLOYMENT="gpt-4"
```

### 2. MCP Server Configuration (Already Set)

The MCP server is already configured in `.env`:

```
MCP_SERVER_URL="https://gitmcp.io/Azure/azure-rest-api-specs"
MCP_SERVER_LABEL="github"
```

You can customize these if you want to use a different MCP server.

## Test Command

```bash
python agents-mcp.py
```

## Expected Behavior

The agent should:

1. Connect to the MCP server at the configured URL
2. Create an agent with MCP tool capabilities
3. Request to summarize Azure REST API specifications README
4. Show tool approval flow (requires manual approval by default)
5. Execute the approved tool call
6. Return the summary

## Notes

- The agent includes tool approval workflow - you may need to approve tool calls during execution
- To disable approval requirement, uncomment the line: `mcp_tool.set_approval_mode("never")`
- The agent dynamically manages allowed tools using `allow_tool()` and `disallow_tool()`
