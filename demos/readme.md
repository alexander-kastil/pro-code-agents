# Designing & Implementing Agents and Pro Code Copilots using Microsoft Agent Framework and Azure AI Agent Service

This in-depth course that takes developers from foundational concepts to advanced multi-agent orchestration using Microsoft's AI ecosystem. The course begins with Azure AI Foundry essentials, covering hubs, projects, and resources while establishing expertise in prompt engineering, GitHub Models, and the Agent-to-Agent (A2A) protocol fundamentals. Students dive deep into Semantic Kernel development, mastering chat completion, multi-modal capabilities, and advanced prompt templating using YAML, Handlebar, and Liquid formats.

The curriculum provides extensive coverage of Semantic Kernel's plugin architecture, including native functions, OpenAPI integrations, and MCP server implementations, alongside Kernel Memory and vector store connectors for RAG solutions. Participants will master both the Semantic Kernel Agent and Process Frameworks, learning to build multi-step task agents with personas while choosing between Orleans and Dapr runtimes. The course emphasizes Azure AI Foundry's multi-agent solutions, teaching students to leverage the Azure AI Foundry Agent Service with action tools (code interpreters, function calling) and knowledge tools (file search, Azure AI Search, Bing Grounding).

Advanced topics include orchestrating complex multi-agent solutions, implementing human-in-the-loop patterns, and integrating .NET Aspire for scalable deployments. The final module ensures production readiness through security, monitoring, and evaluation strategies including agent guardrails, risk monitoring, and Azure AI Foundry's governance and observability features. By completion, students will architect and deploy secure, monitored multi-agent systems leveraging the full power of Azure AI Foundry's orchestration capabilities.

Throughout all modules, you'll work with hands-on code samples in both Python and C#, giving you practical experience building production-ready AI agent solutions.

## Duration

5 Days

## Audience

- Microsoft 365 & AI Pro-Code Developers

## Prerequisites & Requirements

- Basic Microsoft 365 Platform Development Skills
- Basic Azure Development Skills
- Python, C#, Typescript

## Modules

## Module 1: Copilot, Agents & Azure AI Foundry Essentials

### Agent Essentials

- Overview Agents & Agentic AI
- Function Calling & Tools
- Prompt Engineering vs Context Engineering
- Multi Agent Solutions & Orchestration

### Introduction to Azure AI Foundry

- Overview Copilots and Agent Frameworks in the Microsoft Ecosystem
- Hub based projects vs Foundry based Projects
- Deploy Large Language Models (LLM) in Azure AI Foundry
- Azure AI Foundry Model Router
- Visual Studio Code AI Toolkit Extension
- Azure AI Foundry SDK & Microsoft.Extensions.AI
- Deploy AI Apps using Azure Developer CLI

### Implementing Context Servers

- Model Context Protocol (MCP) Overview
- MCP Core Concepts
- Transports STDIO vs Http Streaming
- Develop MCP Servers
- Testing & Debugging using MCP Inspector
- Publishing MCP's to Azure

## Module 2: Develop AI Agents using Microsoft Agent Framework

### Microsoft Agent Framework Basics & Concepts

- Introduction to Microsoft Agent Framework
- Chat Clients vs Agents
- Agent Types & Configuration
- Images & Multi-modal Capabilities
- Structured Output for Chats
- Middleware & Dependency Injection
- Threads, Conversations Persistence & Memory
- Prompt Rendering Middleware
- Supporting Authentication

### Tools & Model Context Protocol

- Understand Tool Call
- Builtin Tools (Code Interpreter, File Search, Web Search)
- Implementing basic Tools
- Use Human in the loop with Tool Call
- Using Function Calling Middleware
- Integrate API's using OpenApi Plugins
- Using existing MCP Tools
- Exposing your Agents as MCP Server

### Knowledge & Retrieval Augmented Generation

- Retrieval Augmented Generation (RAG) vs Agentic RAG
- Agentic Reasoning Process & Self Correction
- Understanding Microsoft.Extensions.AI RAG
- Create Embeddings & using Vector Stores
- Using Azure AI Search Agentic Retrieval

### Microsoft Agent Framework Workflows

- Workflow vs Agents
- Workflow Types & Overview
- Executor & Edges
- Orchestration Patterns (Sequential, Concurrent, ...)
- Branching in Workflows
- Using Agents in Workflows & Workflow as Agents
- Request & Response Handling
- Sharing States & Checkpoints
- Observability & Visualization

## Module 3: Designing & Implementing Agents using Azure AI Foundry Agent Service

### Agent Service Basic Concepts

- Introduction to Azure AI Foundry Agent Service
- Threads, Runs & Messages
- Using Action Tools: Code Interpreter, Function Calling, Azure Functions and OpenAPI Tools
- Using Knowledge Tools: File Search, Azure AI Search
- Deep Research and Bing Grounding
- Connect MCP tools to Azure AI Agent Service
- Automating UI Tasks using Computer Use Agent
- Multi-Agent Workflows & Connected Agents
- Microsoft Agent Framework & Azure AI Foundry Agent Service Integration

### Securing, Monitoring and Evaluating Foundry Agents

- Agent Guardrails and Data Controls
- Ensuring App Behavior using Evaluations
- Monitoring Risk and Alerts
- Azure AI Foundry Agent Governance and Observability

## Module 4: Microsoft Copilot Pro-Code Extensibility

### Pro-Code Agentic Extensibility Options & Fundamentals

- Teams Developer Portal, Microsoft Agent Toolkit & DevTunnel
- App Registrations & Single Sign-On (SSO)
- Pro-Code Agents Overview & Extensibility Options
- Introduction to Microsoft 365 Agent Toolkit & Agent Toolkit CLI
- Pro Code Declarative Agents vs Custom Engine Agents

### Copilot Connectors & Copilot API Capabilities

- Designing & Implementing Copilot Connectors
- Overview Copilot API Capabilities
- Microsoft 365 Copilot Retrieval API

#### Pro-Code Agentic Extensibility Options

- Pro-Code Agents Overview & Extensibility Options
- Introduction to Microsoft 365 Agent Toolkit & Agent Toolkit CLI
- Pro Code Declarative Agents vs Custom Engine Agents
- Custom Engine Agents: Microsoft Agent SDK vs Teams AI Library v2
- When to use which type of Pro-Code Agent

### Declarative Agents for Microsoft 365

- Declarative Agents for Microsoft 365 Copilot Overview
- Creating Declarative Agents using Microsoft 365 Agent Toolkit
- Base Files, Instructions & Conversation Starters
- Knowledge Sources: WebSearch, SharePoint, Teams, ...
- Managing Knowledge & Copilot Connectors
- Adding Skills: Image Generation, Code Interpreter
- Enhance Presentation using Adaptive Cards
- Extend Agents Actions with API Plugins
- Implementing Key-based & EntraID Authentication

### Custom Engine Agents using Microsoft Agent SDK

- Introduction & Benefits of using Microsoft Agent SDK
- Microsoft Agents Playground
- Implementing Custom Engine Agents for Microsoft 365
- Consuming Model Context Protocol (MCP) Tools
- Running Copilot Studio Agents using Microsoft Agent SDK
- Enhance your agent using custom data and Azure AI Search (RAG)
- Integrating Azure AI Foundry Agents in the Copilot UI

### Custom Engine Agents using the Teams AI Library

- Introduction & Benefits of using Teams AI Library
- Create a custom engine agent using Teams AI Library
- Understanding Project Structure & Metadata

### Publishing & Monitoring Pro Code Agents

- Copilot Security & Compliance
- Introduction to Copilot Controls
- Publish and Analyze Pro-Code Agents
