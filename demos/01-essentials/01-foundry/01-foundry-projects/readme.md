# Getting Started with Microsoft Foundry Projects

This guide demonstrates how to deploy and manage AI applications using Microsoft Foundry and the Azure Developer CLI (azd).

## What is Microsoft Foundry?

[Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/what-is-azure-ai-foundry) is a unified platform for developing and deploying generative AI applications and agents. It provides:

- **Foundry Projects** - Collaborative workspaces for AI development with access to models, agents, data, and compute resources
- **Agent Service** - Build and deploy intelligent agents with built-in tools and knowledge capabilities
- **Model Catalog** - Access to 1,600+ models from Microsoft, OpenAI, and partners
- **Evaluations** - Built-in tools to assess agent and model performance
- **Enterprise Security** - Role-based access control, managed identities, and network isolation

## Getting Started with AI Agents Template

The [Get Started with AI Agents](https://github.com/Azure-Samples/get-started-with-ai-agents) template provides a complete solution for building conversational AI agents using Microsoft Foundry Agent Service.

### Prerequisites

Install the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview):

```bash
winget install Microsoft.Azd
```

### Quick Deployment

Deploy the template in one command:

```bash
azd init --template Azure-Samples/get-started-with-ai-agents
azd up
```

| [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/get-started-with-ai-agents) | [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Azure-Samples/get-started-with-ai-agents) |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

### What Gets Deployed

This template creates a complete Azure AI solution:

| Resource                                                                                                         | Description                                                       |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [Microsoft Foundry Project](https://learn.microsoft.com/azure/ai-foundry/how-to/create-projects)                 | Workspace for AI development with agents, models, and evaluations |
| [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)                                    | Powers the AI agents with GPT models (default: gpt-4o-mini)       |
| [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)                                        | Hosts the web application with serverless containers              |
| [Azure Container Registry](https://learn.microsoft.com/azure/container-registry/)                                | Stores and manages container images                               |
| [Storage Account](https://learn.microsoft.com/azure/storage/blobs/)                                              | Provides blob storage for application data and agent files        |
| [Azure AI Search](https://learn.microsoft.com/azure/search/)                                                     | _(Optional)_ Enables hybrid search for knowledge retrieval        |
| [Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)                | _(Optional)_ Provides monitoring and telemetry                    |
| [Log Analytics Workspace](https://learn.microsoft.com/azure/azure-monitor/logs/log-analytics-workspace-overview) | _(Optional)_ Collects and analyzes telemetry data                 |

### Step-by-Step Deployment

1. **Authenticate with Azure**:

   ```bash
   azd auth login
   ```

2. **Initialize the template**:

   ```bash
   azd init --template Azure-Samples/get-started-with-ai-agents
   ```

3. **Deploy to Azure**:
   ```bash
   azd up
   ```

The deployment takes 5-20 minutes and outputs a web app URL when complete.

### Testing Your Agent

After deployment, try these sample questions:

- What's the best tent under $200 for two people, and what features does it include?
- What has David Kim purchased in the past, and based on his buying patterns, what other products might interest him?
- I'm planning a 3-day camping trip for my family. What complete setup would you recommend under $500?

### Configuration Options

#### Optional Services

Disable optional services before deployment:

```bash
azd config set USE_AZURE_AI_SEARCH_SERVICE false
azd config set USE_APPLICATION_INSIGHTS false
```

#### Custom Resource Names

Override default naming conventions:

```bash
azd config set AZURE_OPENAI_NAME <your-openai-name>
azd config set AZURE_SEARCH_SERVICE_NAME <your-search-name>
azd config set AZURE_STORAGE_ACCOUNT_NAME <your-storage-name>
```

## Additional Resources

- **[Azure AI Templates](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/ai-template-get-started)** - Explore more starter templates
- **[Local Development Guide](https://github.com/Azure-Samples/get-started-with-ai-agents/blob/main/docs/local_development.md)** - Customize and run locally
- **[Deployment Guide](https://github.com/Azure-Samples/get-started-with-ai-agents/blob/main/docs/deployment.md)** - Advanced deployment options
- **[Troubleshooting](https://github.com/Azure-Samples/get-started-with-ai-agents/blob/main/docs/troubleshooting.md)** - Common issues and solutions

## Understanding Foundry Projects

Microsoft Foundry supports two types of projects:

- **Foundry Projects** (Recommended) - New resource type with full agent capabilities, Foundry SDK, and unified model access
- **Hub-based Projects** - Legacy projects for specific scenarios like open-source model deployments

For most scenarios, use a **Foundry project** to access the latest features including Microsoft Foundry Agent Service (GA) and the Foundry API.

Learn more: [Choose an Azure resource type for AI Foundry](https://learn.microsoft.com/azure/ai-foundry/concepts/resource-types)
