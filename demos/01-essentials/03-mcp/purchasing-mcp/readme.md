# Purchasing MCP Server

This microservice exposes a small purchasing API used to request price offers from known suppliers and to list supplier information. The README below focuses on what the service does and how the code behaves at runtime (endpoints, request/response shapes and business logic), not on installation or deployment.

Server Description:

```plaintext
Helps with finding suppliers, requesting offers (inquires),
looking up offers, order placement and order tracking.
```

Server Url Endpoints:

```url
http://purchasing-mcp-dev.azurewebsites.net
```

### Run the server

```powershell
dotnet run
```

### Connect with MCP Inspector

1. Start the server (see above).
2. Launch the inspector with the provided config:

```powershell
npx @modelcontextprotocol/inspector --config inspector.config.json --server purchasing-mcp
```

The config at `inspector.config.json` tells the inspector to use the Purchasing MCP server's Streamable HTTP base URL `http://localhost:5151`, matching the endpoint that `app.MapMcp()` exposes. This satisfies the newer CLI requirement that `--server` reference an entry in a config file.

#### Remote (Azure) deployment

```powershell
npx @modelcontextprotocol/inspector --config inspector.config.json --server purchasing-mcp-azure
```

This reuses the same inspector config but selects the `purchasing-mcp-azure-dev` entry, which points at `https://purchasing-mcp-server-dev.azurewebsites.net`. Make sure the Azure app is running and reachable before launching the inspector.

> **Heads-up:** Updating `inspector.config.json` is a local workflow change only—you don’t need to republish the Azure App Service after editing this file. Republish the .NET app itself only when the server code or configuration that lives in the deployed artifact changes.
