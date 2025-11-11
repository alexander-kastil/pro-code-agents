# Develop an Azure AI agent with the Semantic Kernel SDK

## Subprojects

| Folder                      | Language  | Summary                                                                                                                                                                |
| --------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `af-azure-ai-agent`         | .NET (C#) | Minimal Azure AI agent using the Semantic Kernel SDK. Shows core agent bootstrap in `Program.cs`, config via `appsettings.json`, and a simple tool invocation pattern. |
| `af-azure-ai-agent-py`      | Python    | Python equivalent minimal agent using Semantic Kernel Python. Demonstrates lightweight plugin pattern (see `email_plugin.py`) and environment/config separation.       |
| `af-azure-orchestration`    | .NET (C#) | Multi‑agent orchestration sample. Introduces specialized agents (folder `Agents/`), shared services, and plugin tools enabling coordinated task routing.               |
| `af-azure-orchestration-py` | Python    | Python orchestration example with chat driver (`agent_chat.py`) plus custom devops & logging plugins for cross‑agent communication and observability.                  |

## Links & Resources

[Develop an AI agent with Microsoft Agent Framework](https://learn.microsoft.com/en-us/training/modules/develop-ai-agent-with-semantic-kernel/)

[Orchestrate a multi-agent solution using the Microsoft Agent Framework](https://learn.microsoft.com/en-us/training/modules/orchestrate-semantic-kernel-multi-agent-solution/)
