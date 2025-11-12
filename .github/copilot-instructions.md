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

- **Python**: Primary language for Azure AI implementations (azure-ai-projects, azure-ai-inference, azure-ai-evaluation, agent-framework)
- **TypeScript/JavaScript**: Used for web applications and Node.js examples
- **C#/.NET**: Used for some Azure AI Foundry examples
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

### Building and Testing

- **Python Projects**: 
  - Create virtual environments: `python -m venv .venv`
  - Install dependencies: `pip install -r requirements.txt`
  - Main dependencies: azure-ai-projects, azure-ai-inference, azure-ai-evaluation, agent-framework
  
- **Node.js Projects**:
  - Install dependencies: `npm install`
  - Available script: `npm run release` (for versioning)

### Repository Setup

This repository uses Git submodules. When cloning:
```bash
git clone --recursive https://github.com/alexander-kastil/pro-code-agents.git
```

If already cloned without recursive flag:
```bash
git submodule update --init --recursive
```

### Environment Configuration

- Use `create-env.sh` (Linux/Mac) or `create-env.ps1` (Windows) for environment setup
- Store credentials in `.env` files (already gitignored)
- Keep Azure keys and sensitive data in environment variables, never commit them

## Coding Standards

### General Principles

1. **Educational Focus**: Code should be clear and well-documented for learning purposes
2. **Minimal Changes**: When making updates, preserve existing structure and patterns
3. **Documentation**: Update related README.md files when changing demos or examples
4. **Consistency**: Match the coding style of existing files in the same module

### Python Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep Jupyter notebooks clean with clear markdown explanations
- Organize imports: standard library, third-party, local imports

### TypeScript/JavaScript Style

- Use modern ES6+ syntax
- Follow existing formatting conventions in the project
- Add JSDoc comments for complex functions

### Documentation Style

When creating or updating documentation (see `.github/prompts/create-docs.prompt.md`):
- Use clear, concise language
- Include configuration tables for all settings
- Add architecture diagrams for complex components
- Follow the bottom-up documentation approach (service → component → project)
- Use proper markdown code fencing with language identifiers (MD040)

## Custom Prompts

The repository includes custom prompts in `.github/prompts/`:
- `guard.prompt.md`: Basic rules for controlled task execution
- `create-docs.prompt.md`: Template for generating comprehensive documentation
- `playwright.prompt.md`: Guidelines for browser automation tasks

Refer to these when working on specific types of tasks.

## Contributing

When contributing to this repository:

1. **Fork and Branch**: Create a feature branch in your fork
2. **Clear Commits**: Use descriptive commit messages
3. **Pull Requests**: Submit PRs with clear descriptions of changes
4. **Code of Conduct**: Follow the project's Code of Conduct
5. **Licensing**: All work is under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License
6. **Attribution**: Give appropriate credit and maintain license terms

## Important Notes for Copilot

- **Do not modify** existing working demos unless explicitly requested
- **Preserve** the educational structure of examples
- **Keep** code examples simple and clear for learning purposes
- **Test** changes in isolation to avoid breaking other modules
- **Document** all configuration keys and environment variables
- **Respect** the non-commercial nature of the project
- **Follow** existing patterns in each module's subdirectories

## Prerequisites for Running Code

- Python 3.x (with packages from requirements.txt)
- Node.js (for JavaScript/TypeScript examples)
- .NET SDK (for C# examples)
- Azure subscription (for cloud resources)
- Microsoft 365 developer account (for Module 4-5)
- Git with submodules support

## Security Considerations

- Never commit API keys, connection strings, or credentials
- Use `.env` files for local development (already in .gitignore)
- Keep virtual environments (.venv) and node_modules out of version control
- Verify that sensitive data is properly excluded before committing

## Getting Help

- Review module-specific README files for detailed guidance
- Check demo code for working examples
- Refer to custom prompts for task-specific instructions
- Contact the maintainer via LinkedIn or email (see main README.md)
