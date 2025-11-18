# Coding Standards

This directory contains modular coding standards for the Pro Code Agents repository. The standards are organized by technology area to improve clarity and facilitate better context window usage.

## Quick Navigation

### Core Standards

- **[General Standards](general.md)** - Start here for common patterns across all technologies
  - File naming and project structure
  - Documentation and comments
  - Configuration management
  - Error handling
  - Dependency management
  - Security best practices

### Technology-Specific Standards

#### Azure AI Foundry
- **[Azure AI Foundry](azure-ai-foundry.md)** - SDK patterns for Python and C#
  - Client initialization and authentication
  - Chat completions and streaming
  - RAG implementation
  - Embeddings and vector search

#### Agents and Orchestration
- **[Agent Service](agent-service.md)** - Azure AI Foundry Agent Service (Python)
  - Agent creation and configuration
  - Thread and message management
  - Function calling and tools
  - File handling and knowledge bases
  - Multi-agent orchestration

- **[Agent Framework](agent-framework.md)** - Microsoft Agent Framework (Python)
  - Chat interactions and streaming
  - Tools, plugins, and structured output
  - Long-term memory and middleware
  - Workflows and orchestration
  - Multi-agent collaboration

#### Extensibility and Integration
- **[MCP Development](mcp-development.md)** - Model Context Protocol servers (Python & C#)
  - FastMCP framework (Python)
  - Tool definitions and registration
  - Server implementation patterns
  - Deployment and startup scripts

- **[Pro Code Agents](pro-code-agents.md)** - Pro-code extensibility and Microsoft Agents SDK
  - Microsoft 365 Copilot extensibility
  - Custom Engine Agents (C#)
  - Connectors (TypeScript/Node.js)
  - Microsoft Agents SDK integration
  - Service-to-service authentication

#### Educational Content
- **[Jupyter Notebooks](jupyter-notebooks.md)** - Educational notebook guidelines
  - Notebook structure and organization
  - Markdown and code cell standards
  - Interactive examples
  - Visualizations and progress indicators
  - Educational best practices

## Standards by Language

### Python
- [General Standards](general.md) - Configuration, dependencies, testing
- [Azure AI Foundry](azure-ai-foundry.md) - Azure AI SDK patterns
- [Agent Service](agent-service.md) - Agent Service implementation
- [Agent Framework](agent-framework.md) - Agent Framework orchestration
- [MCP Development](mcp-development.md) - MCP server development
- [Jupyter Notebooks](jupyter-notebooks.md) - Notebook guidelines

### C#
- [General Standards](general.md) - Configuration, dependencies, testing
- [Azure AI Foundry](azure-ai-foundry.md) - Azure AI SDK patterns
- [MCP Development](mcp-development.md) - MCP server development
- [Pro Code Agents](pro-code-agents.md) - Custom Engine Agents, Teams bots

### TypeScript/JavaScript
- [Pro Code Agents](pro-code-agents.md) - Connectors and message extensions

## Standards by Module

### Module 1: Essentials
- [Azure AI Foundry](azure-ai-foundry.md) - For SDK and RAG samples
- [Jupyter Notebooks](jupyter-notebooks.md) - For prompt engineering notebooks
- [MCP Development](mcp-development.md) - For MCP server examples

### Module 2: Agent Service
- [Agent Service](agent-service.md) - Primary reference
- [Azure AI Foundry](azure-ai-foundry.md) - Supporting patterns

### Module 3: Agent Framework
- [Agent Framework](agent-framework.md) - Primary reference
- [General Standards](general.md) - Supporting patterns

### Module 4: Copilot Extensibility
- [Pro Code Agents](pro-code-agents.md) - Primary reference
- [MCP Development](mcp-development.md) - For custom tools

### Module 5: Integration
- [Pro Code Agents](pro-code-agents.md) - Primary reference
- [Agent Service](agent-service.md) - For agent integration
- [Agent Framework](agent-framework.md) - For agent orchestration

## Key Principles

All coding standards in this repository follow these principles:

1. **Educational Focus**: Code should be clear and easy to understand for learners
2. **Minimal Complexity**: Avoid over-engineering; keep examples focused
3. **Consistency**: Follow established patterns within each module
4. **Documentation**: Comprehensive comments and README files
5. **Security**: Never commit secrets; use proper authentication

## Configuration Patterns

### Python Projects
- Use `.env` files for configuration
- Provide `.env.copy` templates
- Use `python-dotenv` to load variables
- Maintain both `requirements.txt` and `pyproject.toml`

### C# Projects
- Use `appsettings.json` for configuration
- DO NOT use environment variables or user secrets
- Provide templates with empty sensitive values
- Use .NET 8.0 as target framework

## Getting Help

- For general questions about code organization, see [General Standards](general.md)
- For specific technology questions, see the relevant technology-specific standard
- For questions about educational content, see [Jupyter Notebooks](jupyter-notebooks.md)
- For questions not covered in these standards, refer to the main [copilot-instructions.md](../copilot-instructions.md)

## Contributing

When adding new standards or updating existing ones:

1. Keep standards focused and specific to their technology area
2. Provide complete, working code examples
3. Include both simple and advanced patterns
4. Explain the "why" behind the patterns, not just the "what"
5. Maintain consistency with existing standards
6. Update this README if adding new standard documents
