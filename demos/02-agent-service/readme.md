# Module 2: Implementing Agents using Foundry Agent Service

- Introduction to Foundry Agent Service
- Threads, Runs, Messages: Managing Inputs & Outputs
- Knowledge Integration: File Search, Azure AI Search & Bing Grounding
- Executing Actions with Tools: Code Interpreter, Azure Functions, OpenAPI & MCP
- Automating UI Tasks using Browser Automation and Computer Use
- Tracing, Observability & Performance Evaluation
- Implementing Autonomous Agents
- Agent-to-Agent Protocol (A2A) & Connected Agents

## Demos

| Directory | Demo Name | Description | Key Features |
|-----------|-----------|-------------|--------------|
| [01-agent-basics](./01-agent-basics) | Agent Basics | Introduction to Azure AI Agent Service fundamentals | Creating agents, threads, messages, and basic runs |
| [02-knowledge-tools](./02-knowledge-tools) | Knowledge & Tools | Integrating knowledge sources and tools | File search, function calling, browser automation |
| [03-connected-agents](./03-connected-agents) | Connected Agents | Multi-agent communication using A2A protocol | Agent-to-Agent protocol, orchestration |
| [04-weather-agent](./04-weather-agent) | Weather Agent | Interactive weather assistant with function calling | Custom functions, security filters, interactive chat |

## Links & Resources

---

## Demo Guide: Weather Agent (04-weather-agent)

### Overview

The Weather Agent demonstrates how to build an interactive agent using Azure AI Agent Service with custom function calling capabilities. This demo is a migration from the Agent Framework's DevUI example, showcasing how to implement similar functionality using Azure AI Agent Service.

### What You'll Learn

1. **Function Calling**: How to integrate custom Python functions as agent tools
2. **Security Filters**: Implementing client-side and instruction-based security measures
3. **Interactive Chat**: Building a console-based interactive agent interface
4. **Resource Management**: Proper cleanup of agents and threads

### Features

- **Three Custom Functions**:
  - `get_weather(location)` - Get current weather
  - `get_forecast(location, days)` - Get multi-day forecast
  - `send_email(recipient, subject, body)` - Send notifications (simulated)

- **Security Implementation**:
  - Blocks sensitive data (passwords, secrets, tokens)
  - Restricts access to specific locations (e.g., "Atlantis")
  - Demonstrates both client-side and LLM instruction-based filtering

- **User Experience**:
  - Emoji-enhanced console output
  - UTF-8 support for international characters
  - Conversation history display
  - Graceful shutdown (Ctrl+C or 'quit')

### Key Differences from Agent Framework DevUI

| Aspect | Agent Framework + DevUI | This Demo (Agent Service) |
|--------|------------------------|---------------------------|
| **Interface** | Web-based UI (DevUI) | Interactive console |
| **Middleware** | Native middleware decorators | Implemented via instructions + client logic |
| **Deployment** | Development/testing only | Production-ready service |
| **Function Approval** | `@ai_function(approval_mode)` | Handled through agent design |

### Prerequisites

- Azure AI Foundry project with a deployed model (e.g., GPT-4o)
- Azure credentials configured (`az login`)
- Python 3.11 or higher

### Quick Start

1. **Navigate to the demo directory**:
   ```bash
   cd demos/02-agent-service/04-weather-agent
   ```

2. **Setup environment**:
   ```bash
   cp .env.copy .env
   # Edit .env with your Azure settings
   ```

3. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the agent**:
   ```bash
   python weather_agent.py
   ```

### Example Interactions

**Basic Weather Query**:
```
🌍 You: What's the weather in Seattle?
🤖 Assistant: The weather in Seattle is sunny with a high of 53°C.
```

**Multi-day Forecast**:
```
🌍 You: Give me a 5-day forecast for London
🤖 Assistant: Weather forecast for London:
Day 1: sunny, 54°C
Day 2: sunny, 55°C
Day 3: sunny, 56°C
Day 4: sunny, 57°C
Day 5: sunny, 58°C
```

**Security Filter - Sensitive Data**:
```
🌍 You: What's the weather? My password is secret123
⚠️  Security Alert: I cannot process requests containing sensitive information.
Please rephrase your question without including passwords, secrets, or other sensitive data.
```

**Security Filter - Restricted Location**:
```
🌍 You: What's the weather in Atlantis?
🔒 Blocked! Atlantis is a special place, we must never ask about the weather there!
```

### Architecture

The demo implements a clean separation of concerns:

```
weather_agent.py          # Main agent logic and chat loop
├── Security filters      # Client-side checks for sensitive data
├── AgentsClient setup    # Azure AI Agent Service connection
├── Function tools        # Integration of custom functions
└── Chat loop            # Interactive user interface

weather_functions.py      # Tool implementations
├── get_weather()        # Current weather simulation
├── get_forecast()       # Multi-day forecast simulation
└── send_email()         # Email notification simulation
```

### Configuration

Environment variables (`.env` file):

```bash
PROJECT_ENDPOINT=https://your-project.eastus2.api.azureml.ms
MODEL_DEPLOYMENT=gpt-4o
DELETE_AGENT_ON_EXIT=true
OUTPUT_PATH=./output
```

### Extending the Demo

**Add New Weather Functions**:
1. Define the function in `weather_functions.py`
2. Add it to the `user_functions` set
3. The agent automatically discovers and uses it

**Integrate Real Weather API**:
Replace the simulated data in `get_weather()` and `get_forecast()` with actual API calls to services like OpenWeatherMap or Weather API.

**Add More Security Rules**:
Extend the `blocked_terms` list or add new location restrictions in the client-side filters.

### Troubleshooting

**Authentication Errors**:
- Run `az login` to authenticate
- Verify with `az account show`

**Missing Environment Variables**:
- Ensure `.env` file exists and contains all required values
- Check PROJECT_ENDPOINT format is correct

**Function Call Issues**:
- Verify `azure-ai-agents>=1.2.0b6` is installed
- Ensure `enable_auto_function_calls()` is called before agent creation

### Next Steps

After completing this demo, explore:
- **01-agent-basics**: Learn fundamental agent operations
- **02-knowledge-tools**: Integrate file search and knowledge bases
- **03-connected-agents**: Build multi-agent systems with A2A protocol

### Related Resources

- [Azure AI Agent Service Documentation](https://learn.microsoft.com/azure/ai-services/agents/)
- [Function Calling Best Practices](https://learn.microsoft.com/azure/ai-services/openai/how-to/function-calling)
- [Original Agent Framework DevUI Example](../../03-agent-framework/04-orchestration-workflow/agentfw_workflows-py/)
