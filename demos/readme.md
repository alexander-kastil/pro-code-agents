# Building AI Agents with Microsoft Foundry & Microsoft Agent Framework

This four-day class is crafted for software architects and engineers eager to master the end-to-end process of building, orchestrating, and integrating advanced agentic applications using Microsoft's latest frameworks and services.

The class begins by establishing a strong foundation in Agents, Agentic AI, and the Microsoft Foundry platform. You'll gain hands-on experience deploying large language models, working with the Foundry SDK, and developing robust agentic solutions through prompt- and context engineering, Agentic RAG, ReAct (Reasoning and Acting), and Model Context Protocol (MCP) servers.

From there you move into the Foundry Agent Service—a fully managed, scalable environment for hosting agents. You'll connect knowledge sources including Agent Memory and Foundry IQ, automate workflows with tools such as Code Interpreter, Deep Research, and MCP, and deploy containerized Hosted Agents with dedicated agent identities. Multi-agent coordination is covered through the Agent-to-Agent (A2A) protocol and Connected Agents.

The third day focuses on orchestration and workflow design with the Microsoft Agent Framework. You'll implement Agent Skills using the SKILL.md specification and SkillsProvider, build Durable Agents on Azure Durable Functions for stateful serverless execution, and deploy Hosted Agents to Azure Foundry using container images. Advanced orchestration patterns, checkpointing, human-in-the-loop, and observability complete the picture.

Everything comes together on the final day with the Microsoft 365 Agents SDK, where you'll connect Copilot Studio and Foundry agents via the A2A protocol, orchestrate multi-agent solutions, and publish intelligent agents to Copilot Chat, Teams, and custom front-ends using the AG-UI protocol.

Throughout, hands-on labs and demos in Python and C# ensure practical experience at every step. By the end, you'll be ready to implement, orchestrate, and integrate intelligent pro-code agents—empowering you to deliver scalable, enterprise-grade AI solutions with deep integration into the Microsoft ecosystem.

## Duration

4 Days

## Audience

- Software Architects & Engineers for Agentic AI Solutions
- Microsoft 365 & AI Pro-Code Developers

## Prerequisites & Requirements

- Python, C#, Typescript
- GitHub Account
- Microsoft 365 Development & Azure Development Skills helpful

## Modules

## Module 1: Copilot & Agent Extensibility Fundamentals

### Microsoft Foundry Essentials

- Copilots & Agent Frameworks in the Microsoft Ecosystem
- Deploying LLMs in Microsoft Foundry
- Model Router: Smart Model Selection
- Microsoft Foundry SDK & Microsoft.Extensions.AI
- Infrastructure as Code (IaC) using Azure Developer CLI Agentic Mode

### Agentic AI Fundamentals

- What Are Agents & Agentic AI?
- Prompt Engineering vs Context Engineering
- Knowledge Integration & Agentic RAG
- Deep Reasoning & (Reasoning and Acting)
- Function Calling, REST APIs & MCP Servers
- Evaluating Generative AI Performance
- Governance & Guardrails for Responsible Agents

### Implementing Model Context Protocol Servers (MCP)

- MCP Core Concepts & Architecture
- Transports: STDIO vs HTTP Streaming
- Debugging with MCP Inspector
- Authentication & Security Best Practices
- Hosting MCP's in Azure Functions
- Implementing MCP Apps

## Module 2: Build Agents using Foundry Agent Service

- Introduction to Foundry Agent Service
- Conversations, Runs & State Management
- Knowledge Integration: Foundry IQ, File Search, Azure AI Search, Agent Memory & Bing Grounding
- Executing Actions with Tools: Code Interpreter, Azure Functions, OpenAPI, MCP & Deep Research
- Automating UI Tasks using Browser Automation and Computer Use
- Voice Agent Integration using Azure Speech Voice Live API
- Tracing, Observability & Performance Evaluation
- Hosted Agents: Containerized Deployments with Hosting Adapter & Agent Identity
- Agent-to-Agent Protocol (A2A) & Connected Agents

## Module 3: Orchestrate Agents using Microsoft Agent Framework

### Microsoft Agent Framework Basics & Concepts

- Introduction to the Agent Framework
- Chat Clients vs Agents: Key differences
- Agent types and configuration essentials
- Integrating Microsoft Foundry agents
- Threads, Conversation management & persistence
- Implementing long-term memory
- Governance, Middleware & Observability
- Hosting Agents in ASP.NET Core & Python (AddAIAgent, Responses API)

### Agent Skills & Knowledge

- Agent Skills: SKILL.md structure, SkillsProvider & Progressive Disclosure
- Code-defined Skills vs. File-based Skills
- Agent Skills vs. Workflows: When to use each
- Built-in tools: Code Interpreter, File Search, Bing Grounding
- Adding custom tools and calling them from agents
- Integrating OpenAPI and MCP tools
- Function-calling middleware for advanced workflows

### Orchestration, Durable & Hosted Agents

- Introduction to Multi-Agent Orchestration
- Orchestration Patterns (Sequential, Concurrent, Fan-out/Fan-in)
- Durable Agents with Azure Durable Functions (Flex Consumption, auto-scaling)
- Conversation State Persistence & Durable Task Scheduler
- Hosted Agents: Deploying to Azure Foundry (container images, agent identity)
- Branching, Checkpointing & Human-in-the-loop
- Observability & Workflow Visualization

## Module 4: Agent Integration using Microsoft Agents SDK

- Overview Microsoft 365 Agents SDK (C#, JavaScript, Python)
- Connecting Copilot Studio & Microsoft Foundry Agents via A2A Protocol
- Orchestrate Multi-Agent Solutions using Microsoft Agent Framework
- Publishing Agentic AI Solutions to Copilot Chat and Teams
- Front-End Integration using Agent–User Interaction (AG-UI) Protocol
