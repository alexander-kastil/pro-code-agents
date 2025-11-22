# Azure Weather Agent

A weather assistant agent built using Azure AI Agent Service with function calling capabilities.

## Overview

This demo showcases an interactive weather agent that can:
- Provide current weather information for any location
- Generate multi-day weather forecasts
- Send weather update emails (simulated)
- Implement security filters to block sensitive information and restricted locations

## Features

### Function Calling
The agent uses three custom functions:
- `get_weather(location)`: Get current weather for a location
- `get_forecast(location, days)`: Get multi-day weather forecast
- `send_email(recipient, subject, body)`: Send email notifications (simulated)

### Security Filters
The agent implements security measures through:
- **Sensitive Data Filter**: Blocks requests containing passwords, secrets, API keys, or tokens
- **Location Filter**: Refuses to provide weather for "Atlantis" (demonstration of restricted access)

### Interactive Chat
- Real-time conversation with the weather agent
- UTF-8 support for emoji and special characters
- Graceful exit handling (Ctrl+C or 'quit')
- Conversation history display

## Prerequisites

- Python 3.11 or higher
- Azure AI Foundry project with deployed model
- Azure credentials configured (e.g., via `az login`)

## Setup

1. **Create Environment File**
   ```bash
   cp .env.copy .env
   ```

2. **Configure Azure Settings**
   Edit `.env` and set:
   - `PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
   - `MODEL_DEPLOYMENT`: Your deployed model name (e.g., "gpt-4o")

3. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the weather agent:
```bash
python weather_agent.py
```

### Example Interactions

**Get Current Weather:**
```
You: What's the weather in Seattle?
Assistant: The weather in Seattle is sunny with a high of 53°C.
```

**Get Forecast:**
```
You: Give me a 5-day forecast for London
Assistant: Weather forecast for London:
Day 1: sunny, 54°C
Day 2: sunny, 55°C
Day 3: sunny, 56°C
Day 4: sunny, 57°C
Day 5: sunny, 58°C
```

**Security Filter - Sensitive Data:**
```
You: What's the weather? My password is secret123
Assistant: ⚠️ Security Alert: I cannot process requests containing sensitive information.
```

**Security Filter - Restricted Location:**
```
You: What's the weather in Atlantis?
Assistant: 🔒 Blocked! Atlantis is a special place, we must never ask about the weather there!
```

**Send Email:**
```
You: Send an email to user@example.com about tomorrow's weather
Assistant: Email sent to user@example.com with subject 'Weather Update'. Saved to: ./output/emails/EMAIL-20241122120000.json
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│              (Interactive Console Chat)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Weather Agent                          │
│            (Azure AI Agent Service)                     │
│                                                         │
│  Instructions: Security rules + weather expertise       │
│  Model: GPT-4o (configurable)                          │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐  ┌───────────────────────────┐
│   Security Filters     │  │    Function Tools         │
│  - Sensitive data      │  │  - get_weather()          │
│  - Atlantis blocker    │  │  - get_forecast()         │
└────────────────────────┘  │  - send_email()           │
                            └───────────────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────────┐
                            │  Output (./output/emails) │
                            └───────────────────────────┘
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_ENDPOINT` | Azure AI Foundry project endpoint | Required |
| `MODEL_DEPLOYMENT` | Deployed model name | Required |
| `DELETE_AGENT_ON_EXIT` | Delete agent after exit | `true` |
| `OUTPUT_PATH` | Output directory for emails | `./output` |

## Project Structure

```
04-weather-agent/
├── weather_agent.py          # Main agent implementation
├── weather_functions.py      # Function definitions for tools
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project metadata
├── .env.copy                # Environment template
├── .gitignore               # Git ignore rules
└── readme.md                # This file
```

## Comparison with Agent Framework Version

This demo is a migration from the Agent Framework's DevUI example (`agentfw_weather_devui.py`). Key differences:

| Aspect | Agent Framework + DevUI | Azure AI Agent Service |
|--------|------------------------|------------------------|
| **UI** | Web-based DevUI | Interactive console |
| **Middleware** | Native middleware support | Implemented via instructions |
| **Function Approval** | `@ai_function(approval_mode="always_require")` | Handled by agent logic |
| **Security Filters** | Middleware decorators | Client-side + instruction-based |
| **Deployment** | Development/testing only | Production-ready service |

## Notes

- The weather data is simulated for demonstration purposes
- Email sending is simulated and saves to local JSON files
- Security filters are implemented at both client and agent instruction level
- The agent can be preserved after exit by setting `DELETE_AGENT_ON_EXIT=false`

## Troubleshooting

**Authentication Issues:**
- Ensure you're logged in: `az login`
- Verify credentials: `az account show`

**Missing Environment Variables:**
- Check `.env` file exists and contains required values
- Verify endpoint and model deployment names are correct

**Function Call Errors:**
- Ensure `azure-ai-agents>=1.2.0b6` is installed
- Check that `enable_auto_function_calls()` is called before creating the agent

## See Also

- [Azure AI Agent Service Documentation](https://learn.microsoft.com/azure/ai-services/agents/)
- [Module 2: Agent Service Demos](../)
- [Original Agent Framework DevUI Demo](../../../03-agent-framework/04-orchestration-workflow/agentfw_workflows-py/)
