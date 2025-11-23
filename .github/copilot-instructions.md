# GitHub Copilot Instructions for Pro Code Agents Repository

## Project Overview

This repository contains training materials for a 5-day class on "Implementing Pro Code Agents and Copilots using Microsoft Agent Framework and Azure AI Agent Service". The content is designed for Software Architects & Engineers who want to build, orchestrate, and integrate advanced copilots and agents using Microsoft's frameworks and services.

## Repository Structure

```
.
├── .github/         # GitHub configurations and Copilot prompts
│   └── prompts/     # Custom prompt templates for specific tasks
├── .vscode/         # VS Code settings
├── demos/           # Main training demos organized by module (01-05)
├── labs/            # Hands-on lab exercises
├── setup/           # Setup scripts and configurations
├── src/             # Source code examples
├── tooling/         # Developer tooling and utilities
└── resources/       # Additional learning resources
```

## Tech Stack

- **Python**: Primary language for Azure AI implementations (azure-ai-projects, azure-ai-inference, azure-ai-evaluation, agent-framework) (Python 3.11)
- **TypeScript/JavaScript**: Used for web applications and Node.js examples
- **C# / .NET**: Used for some Azure AI Foundry examples (.NET 10)
- **Azure AI Services**: Azure AI Foundry, Azure AI Agent Service, Azure OpenAI
- **Microsoft Agent Framework**: For building and orchestrating agents
- **Model Context Protocol (MCP)**: For implementing custom servers

## Module Organization

The repository is organized into 5 main modules:

1. **Module 1**: Copilot, Agents & Azure AI Foundry Essentials (demos/01-essentials/)
2. **Module 2**: Implementing Agents using Azure AI Foundry Agent Service (demos/02-agent-service/)
3. **Module 3**: Orchestrating Agents using Microsoft Agent Framework (demos/03-agent-framework/)
4. **Module 4**: Pro-Code Extensibility using Microsoft 365 Agent Toolkit & Custom Engine Agents (demos/04-copilot-extensibility/)
5. **Module 5**: Agent & Copilot Integration using the Microsoft Agents SDK (demos/05-integration/)

## Development Guidelines

## Coding Standards

This repository uses modular coding standards organized by technology area. All standards follow these general principles:

1. **Educational Focus**: Code should be clear and well-documented for learning purposes
2. **Minimal Changes**: When making updates, preserve existing structure and patterns
3. **Documentation**: Update related readme.md files when changing demos or examples (always use lowercase `readme.md`, never `README.md`)
4. **Consistency**: Match the coding style of existing files in the same module
5. **Minimal Error Handling**: Use only absolutely necessary error handling - these are demos and excessive try-catch blocks make code hard to read and understand

### Coding Standards Reference

For detailed coding standards, refer to the following documents in `.github/coding-standards/`:

- **[General Coding Standards](.github/coding-standards/general.md)**
- **[Azure AI Foundry Standards](.github/coding-standards/azure-ai-foundry.md)**
- **[MCP Development Standards](.github/coding-standards/mcp-development.md)**
- **[Agent Service Standards](.github/coding-standards/agent-service.md)**
- **[Agent Framework Standards](.github/coding-standards/agent-framework.md)**
- **[Pro Code Agents & SDK Standards](.github/coding-standards/pro-code-agents.md)**
- **[Jupyter Notebook Standards](.github/coding-standards/jupyter-notebooks.md)**

## Programming Languages / Tech Stack

- [Python Projects](.github/coding-standards/python.md)
- [C# Projects](.github/coding-standards/csharp.md)
- [Jupyter Notebooks](.github/coding-standards/jupyter-notebooks.md)

### Documentation Style

When creating or updating documentation (see `.github/prompts/create-docs.prompt.md`):

- Use clear, concise language
- Include configuration tables for all settings
- Add architecture diagrams for complex components
- Follow the bottom-up documentation approach (service → component → project)
- Use proper markdown code fencing with language identifiers (MD040)
