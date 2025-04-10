# Implementing AI Agents and Copilots using Azure OpenAI

This workshop is designed to help you develop AI agents and copilots using Azure OpenAI. The workshop is divided into four modules, each covering different aspects of developing AI solutions with Azure OpenAI. It bundles the following Microsoft Applied Skills courses and deep dives Semantic Kernel. To provide a full picture of the AI development process, we have added the module on monitoring and deploying LLM applications:

- AI-050 - Develop Generative AI Solutions with Azure OpenAI Service
- AI-3016 - Develop custom copilots with Azure AI Studio
- AI-2005 - Develop AI Agents using Azure OpenAI and the Semantic Kernel SDK

Module 1: Develop Generative AI Solutions with Azure OpenAI Service

This module introduces Azure OpenAI Service, covering how to access and use it, explore generative AI models, and deploy them. It explains the differences between completions and chat, and how to use prompts to get completions from models. Additionally, it guides testing models in Azure OpenAI Studio’s playgrounds and integrating Azure OpenAI into applications using REST API and SDK. The module also delves into prompt engineering, generating code and images, implementing Retrieval Augmented Generation (RAG), and planning responsible generative AI solutions.

Module 2: Develop custom Copilots with Azure AI Studio

This module provides an introduction to Azure AI Studio, highlighting its core features, capabilities, and use cases. It explains how to build a RAG-based copilot solution with your own data, and the basics of developing copilots with Prompt Flow. The module covers integrating a fine-tuned language model with your copilot and evaluating its performance. It emphasizes the importance of understanding the development lifecycle and using LangChain in Prompt Flow.

Module 3: Develop AI agents using Azure OpenAI and the Semantic Kernel SDK

This module focuses on building AI agents using the Semantic Kernel SDK, starting with understanding the purpose of Semantic Kernel and effective prompting techniques. It explains how to give AI agents skills using Native Functions and create plugins for Semantic Kernel. The module also covers providing state and history using Kernel Memory, using intelligent planners, and integrating various AI services with Semantic Kernel. Additionally, it discusses implementing copilots and agents, completing multi-step tasks, and using personas with agents.

Module 4: Monitoring & Deploying LLM Applications

This module outlines the deployment process for LLM applications, including introductions to Azure Container Apps and how to deploy LLM applications to them. It explains how to scale Azure OpenAI for .NET chat using RAG with Azure Container Apps and manage dynamic sessions with LangChain. The module also covers exposing LLM apps using Azure API Management and monitoring and managing LLM applications to ensure optimal performance.

## Module 1: Develop Generative AI Solutions with Azure OpenAI Service

### Get started with Azure OpenAI Service

- Access Azure OpenAI Service
- Use Azure OpenAI Studio
- Explore types of generative AI models
- Deploy generative AI models
- Completions vs Chat
- Use prompts to get completions from models
- Test models in Azure OpenAI Studio's playgrounds

## Build natural language solutions with Azure OpenAI Service

- Integrate Azure OpenAI into your app
- Use Azure OpenAI REST API
- Use Azure OpenAI SDK

## Apply prompt engineering with Azure OpenAI Service

- Understand prompt engineering
- Write more effective prompts
- Zero-shot- vs Few-shot learning
- Chain-of-thought prompting 
- Provide context to improve accuracy
- System Messages
- Function Calling

# Generate code with Azure OpenAI Service

- Construct code from natural language
- Complete code and assist the development process
- Fix bugs and improve your code

# Generate images with Azure OpenAI Service

- What is DALL-E?
- Explore DALL-E in Azure OpenAI Studio
- Use the Azure OpenAI REST API to consume DALL-E models

# Implement Retrieval Augmented Generation (RAG) with Azure OpenAI Service

- Understand Retrieval Augmented Generation (RAG) with Azure OpenAI Service
- Add your own data source
- Chat with your model using your own data

# Fundamentals of Responsible Generative AI

- Plan a responsible generative AI solution
- Identify potential harms
- Measure potential harms
- Mitigate potential harms
- Operate a responsible generative AI solution

## Module 2: Develop custom Copilots with Azure AI Studio

### Introduction to Azure AI Studio

- Core Features and Capabilities of Azure AI Studio
- Azure AI Hubs & Projects
- Provision and manage an Azure AI Resources
- Azure AI Studio: Use Cases and Scenarios

### Build a RAG-based copilot solution with your own data using Azure AI Studio

- Identify the need to ground your language model with Retrieval Augmented Generation (RAG)
- Index your data with Azure AI Search to make it searchable for language models
- Build a copilot using RAG on your own data in the Azure AI Studio
- Using RAG in Prompt Flow

## Introduction to developing Copilots with Prompt Flow in the Azure AI Studio

- Prompt-Flow Overview, Integration and Use Cases
- Understand Prompt Flow Basics and Core Components
- Using Prompt Flow Variants
- Understand the Development Lifecycle when Creating Language Model Applications.
- Using LangChain in Prompt Flow

## Integrate a fine-tuned language model with your copilot in the Azure AI Studio

- Fine Tuning Overview 
- When to use fine-tuning
- Fine-tune a language model in the Azure AI Studio

### Evaluate the performance of you custom copilot in the Azure AI Studio

- Assess the model performance
- Understand model benchmarks
- Using evaluations to monitor and improve your model

## Module 3: Develop AI agents using Azure OpenAI and the Semantic Kernel SDK

### Build your kernel

- Understand the purpose of Semantic Kernel
- Understand prompting basics & techniques for more effective prompts
- Use OpenAI, Azure OpenAI & 3rd party Large Language Models

### Give your AI agent skills using Native Functions

- Understand Native Functions in the Semantic Kernel SDK
- Implement Native Functions using Prompts
- Using yaml based prompts
- Chaining Native Functions
- Using Pre- and Post Hooks

### Create Plugins for Semantic Kernel

- Understand the purpose of Semantic Kernel plugins
- Built-in plugins (ConversationSummary, FileIO, Http, Math, Time)
- Implementing data retrieval and task automation plugins
- Persisting Data using Plugins

### Providing state & history using Kernel Memory

- Understand the purpose of Kernel Memory 
- Semantic Kernel Memory: In-process & Connectors
- High performance memory using Azure Cosmos DB DiskANN
- Kernel Memory & Retrieval Augmented Generation (RAG)
- Streaming Responses to Single Page Applications

### Use intelligent planners

- Understand planners in the Semantic Kernel SDK
- Use & optimize planners to automate function calls
- Learn how to use Semantic Kernel SDK to automatically invoke functions
- Function calling as a planner replacement
- Automatic vs Manual Function Calling
- Using Function Filters and Function Calling Helpers

### Integrating AI Services with Semantic Kernel

- Text to Image & Image to Text
- Using Audio to Text
- Using Hugging Face with Semantic Kernel
- Integrating Prompt-Flow with Semantic Kernel

### Implementing Copilots & Assistant using Semantic Kernel

- Assistant Overview
- OpenAI Assistant Specification
- Completing multi-step tasks with Assistant
- Using Personas with Assistant
- Implementing Multi Assistant Solutions

## Module 4: Monitoring & Deploying LLM Applications

- Understand the deployment process for LLM applications
- Introductions to Azure Container Apps
- Deploy LLM applications to Azure Container Apps
- Scale Azure OpenAI Apps with Azure Container Apps
- Azure Container Apps Dynamic Sessions
- Monitor and manage LLM applications