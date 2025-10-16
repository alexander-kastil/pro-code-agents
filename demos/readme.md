# Implementing Agents and Copilots using Semantic Kernel and Azure AI Foundry Agent Service

This in-depth course that takes developers from foundational concepts to advanced multi-agent orchestration using Microsoft's AI ecosystem. The course begins with Azure AI Foundry essentials, covering hubs, projects, and resources while establishing expertise in prompt engineering, GitHub Models, and the Agent-to-Agent (A2A) protocol fundamentals. Students dive deep into Semantic Kernel development, mastering chat completion, multi-modal capabilities, and advanced prompt templating using YAML, Handlebar, and Liquid formats.

The curriculum provides extensive coverage of Semantic Kernel's plugin architecture, including native functions, OpenAPI integrations, and MCP server implementations, alongside Kernel Memory and vector store connectors for RAG solutions. Participants will master both the Semantic Kernel Agent and Process Frameworks, learning to build multi-step task agents with personas while choosing between Orleans and Dapr runtimes. The course emphasizes Azure AI Foundry's multi-agent solutions, teaching students to leverage the Azure AI Foundry Agent Service with action tools (code interpreters, function calling) and knowledge tools (file search, Azure AI Search, Bing Grounding).

Advanced topics include orchestrating complex multi-agent solutions, implementing human-in-the-loop patterns, and integrating .NET Aspire for scalable deployments. The final module ensures production readiness through security, monitoring, and evaluation strategies including agent guardrails, risk monitoring, and Azure AI Foundry's governance and observability features. By completion, students will architect and deploy secure, monitored multi-agent systems leveraging the full power of Azure AI Foundry's orchestration capabilities.

Throughout all modules, you'll work with hands-on code samples in both Python and C#, giving you practical experience building production-ready AI agent solutions.

## Audience

- Microsoft 365 & AI Pro-Code Developers

## Prerequisites & Requirements

- Basic Microsoft 365 Platform Development Skills
- Basic Azure Development Skills
- Python, C#, Typescript

## Modules

## Module 1: Copilot, Agents & Azure AI Foundry Essentials

### Introduction to Azure AI Foundry

- Overview Copilots and Agent Frameworks in the Microsoft Ecosystem
- Azure AI Foundry: Hubs, Projects and Resources
- Hub based projects vs AI Foundry Projects
- Deploy and use Large Language Models (LLM) in Azure AI Foundry
- Visual Studio Code AI Toolkit Extension
- Introduction to Azure AI Foundry SDK
- Deploy AI Apps using Azure Developer CLI

### Agent Essentials

- Introduction Effective Prompt Engineering
- Introduction to GitHub Models
- Comparing and Prototyping Prompts using GitHub Models
- Retrieval Augmented Generation (RAG) & Agentic Retrieval in Azure AI Search
- Function Calling

### Developing & Consuming Model Context Servers

- Model Context Protocol (MCP) Overview
- MCP Core Concepts
- Transports STDIO vs Http Streaming
- Develop MCP Servers
- Testing & Debugging using MCP Inspector
- Publishing MCP's to Azure

## Module 2: Develop AI Agents using Microsoft Agent Framework

### Microsoft Agent Framework Basics & Concepts

- Introduction to Microsoft Agent Framework
- Chat History & AI Services Integration
- ChatCompletion and Multi-modal capabilities
- Configuration & Dependency Injection

### Optimizing Prompts

- Prompt Engineering with Semantic Kernel
- YAML Prompt Templates and Template Formats
- Handlebar Prompt Templates
- Liquid Prompt Templates
- Using Prompty Visual Studio Code Extension

### Implement Plugins for Semantic Kernel

- Understand the purpose of Semantic Kernel plugins
- Learn how to use pre-made plugins
- Planners, Function Calling and Choice Behaviors
- Implement Native Functions using Prompts
- Integrate existing API's using OpenApi Plugins
- Using MCP Servers in Semantic Kernel
- Invocation-, Prompt Render & Invocation Filters

### Kernel Memory & Vector Store Connectors

- Understand the purpose of Kernel Memory
- Semantic Kernel Memory: In-process & Out-of-the-box-Connectors
- Data Model And Embedding Generation
- Kernel Memory & Retrieval Augmented Generation (RAG)

## Semantic Kernel Agent Framework

- Agents Overview
- Completing multi-step tasks with Agents
- Using Personas with Agents
- Implementing Multi Agent Solutions
- Sematic Kernel A2A Integration
- Using .NET Aspire in multi-agent scenarios

## Semantic Kernel Process Framework

- Process Framework Overview
- Core Components and Patterns
- Runtimes: Orleans vs Dapr
- Implementing Human in the Loop

## Module 3: Develop Agents using Azure AI Foundry Agent Service

- Introduction to Azure AI Foundry Agent Service
- Using Action Tools: Code Interpreter, Function Calling, Azure Functions and OpenAPI Tools
- Using Knowledge Tools: File Search, Azure AI Search and Bing Grounding
- Connect MCP tools to Azure AI Agent Service
- Automating UI Tasks using Computer Use Agent
- Designing and implementing connected Agents
- Orchestrate Multi-Agent-Solutions using Semantic Kernel

## Module 4: Securing, Monitoring and Evaluating Foundry Agents

- Agent Guardrails and Data Controls
- Ensuring App Behavior using Evaluations
- Monitoring Risk and Alerts
- Azure AI Foundry Agent Governance and Observability

## Module 5: Microsoft Copilot Pro-Code Extensibility

#### Pro-Code Extensibility Fundamentals

- Teams Developer Portal, Microsoft Agent Toolkit & DevTunnel
- App Registrations & Single Sign-On (SSO)
- Azure Resources Deployment using Azure Developer CLI & Bicep

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

#### Declarative Agents for Microsoft 365

- Declarative Agents for Microsoft 365 Copilot Overview
- Creating Declarative Agents using Microsoft 365 Agent Toolkit
- Base Files, Instructions & Conversation Starters
- Knowledge Sources: WebSearch, SharePoint, Teams, ...
- Managing Knowledge & Copilot Connectors
- Adding Skills: Image Generation, Code Interpreter
- Enhance Presentation using Adaptive Cards
- Debugging & Fixing Errors GitHub Copilot
- Declarative Agents using TypeSpec
- Extend Agents Actions with API Plugins
- Implementing Key-based & EntraID Authentication

#### Custom Engine Agents using Microsoft Agent SDK

- Introduction & Benefits of using Microsoft Agent SDK
- Microsoft Agents Playground
- Implementing Custom Engine Agents for Microsoft 365
- Consuming Model Context Protocol (MCP) Tool
- Running Copilot Studio Agents using Microsoft Agent SDK
- Enhance your agent using custom data and Azure AI Search (RAG)
- Integrating Azure AI Foundry Agents in the Copilot UI

#### Custom Engine Agents using the Teams AI Library

- Introduction & Benefits of using Teams AI Library
- Create a custom engine agent using Teams AI Library
- Understanding Project Structure & Metadata
- Activity Handling
- Integrate Enterprise data using RAG

#### Publishing & Monitoring Pro Code Agents

- Copilot Security & Compliance
- Introduction to Copilot Controls
- Publish and Analyze Pro-Code Agents
