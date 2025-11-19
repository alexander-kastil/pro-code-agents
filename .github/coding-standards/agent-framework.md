# Microsoft Agent Framework Coding Standards

## Overview

This document provides coding standards for building agents using the Microsoft Agent Framework. The Agent Framework is a Python library for orchestrating agents with support for tools, knowledge, workflows, and multi-agent systems.

## Python Standards

### Environment Setup

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AZURE_AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_AI_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
```

### Client Initialization

#### Basic Agent Client

```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

async with AzureCliCredential() as credential:
    async with AIProjectClient(
        endpoint=AZURE_AI_PROJECT_ENDPOINT,
        credential=credential
    ) as project_client:
        
        async with ChatAgent(
            chat_client=AzureAIAgentClient(
                project_client=project_client,
                agent_id=agent_id,
                async_credential=credential
            )
        ) as agent:
            # Use agent here
            pass
```

### Creating Agents

#### Create New Agent in Azure AI Foundry

```python
from azure.ai.agents.aio import AgentsClient

async with AgentsClient(
    endpoint=AZURE_AI_PROJECT_ENDPOINT,
    credential=credential
) as agents_client:
    
    created_agent = await agents_client.create_agent(
        model=AZURE_AI_MODEL_DEPLOYMENT_NAME,
        name="My Agent",
        instructions="You are a helpful AI assistant.",
        description="Agent created by Agent Framework"
    )
    
    print(f"Agent ID: {created_agent.id}")
```

#### Use Existing Agent

```python
async with ChatAgent(
    chat_client=AzureAIAgentClient(
        project_client=project_client,
        agent_id="existing-agent-id",
        async_credential=credential
    )
) as agent:
    response = await agent.send_message("Hello!")
    print(response.content)
```

### Chat Interactions

#### Simple Chat

```python
async with ChatAgent(chat_client=client) as agent:
    response = await agent.send_message("What is the weather today?")
    print(response.content)
```

#### Interactive Chat Loop

```python
async with ChatAgent(chat_client=client) as agent:
    print("Interactive Chat (Type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        response = await agent.send_message(user_input)
        print(f"\nAgent: {response.content}")
```

#### Streaming Responses

```python
async with ChatAgent(chat_client=client) as agent:
    print("Agent: ", end="", flush=True)
    
    async for chunk in agent.send_message_stream("Tell me a story"):
        print(chunk.content, end="", flush=True)
    
    print()  # New line after streaming
```

### Chat History

```python
# Get conversation history
history = agent.get_chat_history()

for message in history:
    print(f"{message.role}: {message.content}")

# Clear history
agent.clear_chat_history()
```

### Multimodal Input

#### Image Input

```python
import base64

# Load and encode image
with open("image.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Send message with image
response = await agent.send_message(
    content="What's in this image?",
    images=[{
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{image_data}"
        }
    }]
)
```

#### File Input

```python
# Upload file to Azure AI Foundry
with open("document.pdf", "rb") as f:
    file = await project_client.agents.files.upload(
        file=f,
        purpose="assistants"
    )

# Reference file in message
response = await agent.send_message(
    content="Summarize this document",
    file_ids=[file.id]
)
```

### Structured Output

```python
from pydantic import BaseModel

# Define output schema
class WeatherResponse(BaseModel):
    location: str
    temperature: float
    conditions: str
    forecast: str

# Request structured output
response = await agent.send_message(
    content="What's the weather in Seattle?",
    response_format=WeatherResponse
)

# Access structured data
weather = response.parsed
print(f"Temperature: {weather.temperature}°F")
```

### Tools and Plugins

#### Define Tools

```python
from typing import Annotated

def get_current_weather(
    location: Annotated[str, "The city and state, e.g., San Francisco, CA"]
) -> str:
    """Get the current weather for a location."""
    # Implementation
    return f"The weather in {location} is sunny."

def calculate_distance(
    start: Annotated[str, "Starting location"],
    end: Annotated[str, "Ending location"]
) -> float:
    """Calculate distance between two locations."""
    # Implementation
    return 42.5
```

#### Register Tools with Agent

```python
from agent_framework.tools import ToolRegistry

# Create tool registry
tools = ToolRegistry()
tools.register(get_current_weather)
tools.register(calculate_distance)

# Create agent with tools
async with ChatAgent(
    chat_client=client,
    tools=tools
) as agent:
    response = await agent.send_message("What's the weather in Seattle?")
    print(response.content)
```

### Long-Term Memory

```python
from agent_framework.memory import Memory

# Create agent with memory
async with ChatAgent(
    chat_client=client,
    memory=Memory(
        project_client=project_client,
        vector_store_name="agent-memory"
    )
) as agent:
    
    # Agent will remember across sessions
    await agent.send_message("My name is John")
    
    # Later...
    response = await agent.send_message("What's my name?")
    print(response.content)  # Should remember "John"
```

### Middleware

```python
from agent_framework.middleware import Middleware

class LoggingMiddleware(Middleware):
    """Log all agent interactions."""
    
    async def on_request(self, message: str):
        """Called before sending message to agent."""
        print(f"[Request] {message}")
    
    async def on_response(self, response: str):
        """Called after receiving response from agent."""
        print(f"[Response] {response}")
    
    async def on_tool_call(self, tool_name: str, args: dict):
        """Called when agent uses a tool."""
        print(f"[Tool Call] {tool_name}({args})")

# Use middleware
async with ChatAgent(
    chat_client=client,
    middleware=[LoggingMiddleware()]
) as agent:
    response = await agent.send_message("Hello!")
```

### Workflows and Orchestration

#### Sequential Workflow

```python
from agent_framework.workflow import Workflow, Step

workflow = Workflow()

# Define workflow steps
@workflow.step()
async def analyze_request(context):
    """Analyze the user request."""
    response = await agent.send_message(
        f"Analyze this request: {context.input}"
    )
    context.analysis = response.content
    return context

@workflow.step()
async def generate_response(context):
    """Generate final response based on analysis."""
    response = await agent.send_message(
        f"Based on this analysis: {context.analysis}, generate a response"
    )
    context.output = response.content
    return context

# Run workflow
result = await workflow.run(input="Create a marketing plan")
print(result.output)
```

#### Conditional Workflow

```python
@workflow.step()
async def route_request(context):
    """Route based on request type."""
    if "weather" in context.input.lower():
        context.next_step = "handle_weather"
    elif "math" in context.input.lower():
        context.next_step = "handle_math"
    else:
        context.next_step = "handle_general"
    return context

@workflow.step(condition=lambda ctx: ctx.next_step == "handle_weather")
async def handle_weather(context):
    """Handle weather requests."""
    # Implementation
    pass
```

#### Parallel Workflow

```python
import asyncio

async def run_parallel_tasks():
    """Run multiple agent tasks in parallel."""
    
    tasks = [
        agent1.send_message("Task 1"),
        agent2.send_message("Task 2"),
        agent3.send_message("Task 3")
    ]
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"Task {i+1} result: {result.content}")
```

### Multi-Agent Orchestration

#### Agent Handoff

```python
# Create specialist agents
weather_agent = ChatAgent(chat_client=weather_client)
calendar_agent = ChatAgent(chat_client=calendar_client)

# Orchestrator logic
async def orchestrate(user_request: str):
    """Route request to appropriate agent."""
    
    if "weather" in user_request.lower():
        return await weather_agent.send_message(user_request)
    elif "calendar" in user_request.lower():
        return await calendar_agent.send_message(user_request)
    else:
        return "I'm not sure which agent can help with that."

# Use orchestrator
response = await orchestrate("What's the weather today?")
```

#### Agent Collaboration

```python
async def collaborative_task(query: str):
    """Multiple agents work together on a task."""
    
    # Step 1: Research agent gathers information
    research = await research_agent.send_message(
        f"Research: {query}"
    )
    
    # Step 2: Analysis agent analyzes the research
    analysis = await analysis_agent.send_message(
        f"Analyze this research: {research.content}"
    )
    
    # Step 3: Writer agent creates final output
    final_output = await writer_agent.send_message(
        f"Write a report based on this analysis: {analysis.content}"
    )
    
    return final_output.content
```

### Observability

```python
import logging
from agent_framework.observability import Tracer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use tracer
tracer = Tracer(name="my-agent")

async with tracer.span("agent-interaction"):
    response = await agent.send_message("Hello")
    tracer.log("message-sent", {"content": "Hello"})
    tracer.log("response-received", {"content": response.content})
```

### Error Handling

```python
from agent_framework.exceptions import AgentError, ToolExecutionError

try:
    response = await agent.send_message("Hello")
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
    # Handle tool error
except AgentError as e:
    print(f"Agent error: {e}")
    # Handle agent error
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

## Best Practices

### Agent Design

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Clear Instructions**: Write specific, detailed instructions for each agent
3. **Tool Selection**: Only include tools the agent actually needs
4. **State Management**: Use memory and context appropriately

### Async Patterns

1. **Always Use Async**: Agent Framework is async-first
2. **Context Managers**: Always use `async with` for proper cleanup
3. **Gather Parallel Tasks**: Use `asyncio.gather()` for concurrent operations
4. **Error Handling**: Handle async errors appropriately

### Performance

1. **Connection Pooling**: Reuse clients when possible
2. **Batch Operations**: Combine multiple operations when appropriate
3. **Streaming**: Use streaming for long responses
4. **Resource Cleanup**: Always close agents and clients properly

### Debugging

1. **Enable Logging**: Use Python logging for debugging
2. **Trace Workflows**: Log all workflow steps
3. **Monitor Tool Calls**: Track which tools are being called
4. **Inspect Chat History**: Review conversation history for issues

### Educational Focus

When creating demos:

- Start with simple examples and build up complexity
- Comment on async patterns and why they're used
- Show error handling examples
- Demonstrate cleanup and resource management
- Include interactive examples for hands-on learning
