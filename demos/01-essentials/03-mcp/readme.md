# Implementing Model Context Protocol Servers

- Model Context Protocol (MCP) Overview
- MCP Core Concepts
- Transports STDIO vs Http Streaming
- Develop MCP Servers
- Testing & Debugging using MCP Inspector
- Publishing MCP's to Azure

## Links & Resources

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)

[MCP Servers](https://github.com/modelcontextprotocol/servers)

# Model Context Protocol (MCP) Demos

[Remote MCP with Azure Functions (.NET/C#)](https://learn.microsoft.com/en-us/samples/azure-samples/remote-mcp-functions-dotnet/remote-mcp-functions-dotnet/)

[Remote MCP with Azure Functions (Python)](https://learn.microsoft.com/en-us/samples/azure-samples/remote-mcp-functions-python/remote-mcp-functions-python/)

[Remote MCP with Azure Functions (Node.js/TypeScript/JavaScript)](https://learn.microsoft.com/en-us/samples/azure-samples/remote-mcp-functions-typescript/remote-mcp-functions-typescript/)

## Demo

> Note: Ensure [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd) is installed

Clone the base repository while in beta:

```bash
azd init --template "https://github.com/azure-samples/remote-mcp-functions-typescript/tree/main/"
```

Implement your function

Run the function:

```bash
func start
```

Create the dev tunnel:

```bash
devtunnel login
devtunnel create hr-mcp-copilot-studio -a --host-header unchanged
devtunnel port update hr-mcp-copilot-studio -p 47002
devtunnel host hr-mcp-copilot-studio
```

Run MCP inspector:

```bash
npx @modelcontextprotocol/inspector
```

In the MCP inspector, connect to the MCP server and choose `List Tools` and then use the `list_candidates` tool:

- Transport Type: `Streamable Http`
- Endpoint URL: `https://hr-mcp-copilot-studio.<your-dev-tunnel-id>.devtunnels.ms`
- Port: `47002`

> Note: If you want you can publish the web app to avoid using the dev tunnel, but this is not required for the demo.
