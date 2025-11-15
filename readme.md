# Building Pro-Code Copilots and Agentic Apps with Azure AI Foundry & Microsoft Agent Framework

Companion Material for Class Delivery by [Alexander Kastil](https://www.linkedin.com/in/alexander-kastil-3bb26511a/) containing:

- [Module 1: Copilot & Agent Extensibility Fundamentals](./demos/01-essentials/)
- [Module 2: Building Agents using Azure AI Foundry Agent Service](./demos/02-agent-service)
- [Module 3: Orchestrating Agents using Microsoft Agent Framework](./demos/03-agent-framework)
- [Module 4: Pro-Code Extensibility using Microsoft 365 Agent Toolkit & Custom Engine Agents](./demos/04-copilot-extensibility/)
- [Module 5: Agent & Copilot Integration using the Microsoft Agents SDK](./demos/05-integration)

## Pending .NET 10 Migration

The following projects still target .NET versions below 10 and need migration:

- [ ] [demos/04-copilot-extensibility/02-connectors-api/02-connectors/dotnet/parts-inventory/PartsInventoryConnector.csproj](demos/04-copilot-extensibility/02-connectors-api/02-connectors/dotnet/parts-inventory/PartsInventoryConnector.csproj)
- [ ] [demos/04-copilot-extensibility/03-agents/01-intro/01-semantic-kernel/sk-email-agent/email-agent.csproj](demos/04-copilot-extensibility/03-agents/01-intro/01-semantic-kernel/sk-email-agent/email-agent.csproj)
- [ ] [demos/04-copilot-extensibility/03-agents/01-intro/01-semantic-kernel/sk-mcp-tooling/sk-use-mcp.csproj](demos/04-copilot-extensibility/03-agents/01-intro/01-semantic-kernel/sk-mcp-tooling/sk-use-mcp.csproj)
- [ ] [demos/05-integration/02-m365-agents-sdk/weather-agent-vs-sk/weather-agent-vs.csproj](demos/05-integration/02-m365-agents-sdk/weather-agent-vs-sk/weather-agent-vs.csproj)
- [ ] [demos/05-integration/03-agent-framework/hr-agent-vs/ContosoHRAgent.csproj](demos/05-integration/03-agent-framework/hr-agent-vs/ContosoHRAgent.csproj)
- [ ] [labs/01-essentials/03-mcp/cs/remote-mcp-functions-dotnet/src/FunctionsMcpTool.csproj](labs/01-essentials/03-mcp/cs/remote-mcp-functions-dotnet/src/FunctionsMcpTool.csproj) (currently net8.0, Azure Functions)

## Cloning the Repository

This repository uses Git submodules. To clone the repository and automatically download all submodules, use:

```bash
git clone --recursive https://github.com/alexander-kastil/pro-code-agents.git
```

If you have already cloned the repository without `--recursive`, you can initialize and update the submodules with:

```bash
git submodule update --init --recursive
```

## Contributing

Feel free to contribute. When contribute implement your changes / additions on a feature branch in your fork and issue a pull request after completion. An introduction video into forks and pull requests can be found [here](https://www.youtube.com/watch?v=nT8KGYVurIU)

## License & Re-Use

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License

Permission is hereby granted to to use, modify, and distribute the workshop materials provided under the following conditions:

- Personal Use: Users may use the materials for personal learning and educational purposes.
- Modification: Users may modify the materials to suit their needs.
- Non-Commercial Use: Commercial use is strictly prohibited.
- Attribution: Users must give appropriate credit to the author and include a link to the original materials.
- Share-Alike: Any derivative works based on these materials must be shared under the same license terms.

For commercial use please contact the author via [LinkedIn](https://www.linkedin.com/in/alexander-kastil-3bb26511a/) or [email](mailto:alexander.kastil@integrations.at)
