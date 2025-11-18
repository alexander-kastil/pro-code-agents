# Pro Code Agents and Microsoft Agents SDK Coding Standards

## Overview

This document covers coding standards for pro-code agent development and integration using the Microsoft Agents SDK. This includes building custom engine agents, copilot extensions, and integrating agents into applications.

## Microsoft 365 Copilot Extensibility

### Declarative Agents

#### Agent Manifest

```json
{
  "name": "Product Support Agent",
  "description": "Assists with product support queries",
  "instructions": "You are a product support specialist. Help users with product issues.",
  "conversation_starters": [
    "How do I reset my password?",
    "What are your support hours?",
    "I have a problem with my order"
  ],
  "actions": [
    {
      "id": "searchKnowledgeBase",
      "file": "./actions/search.json"
    }
  ],
  "capabilities": {
    "web_search": true,
    "file_upload": true
  }
}
```

### API Plugins

#### OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: Product API
  description: API for product information
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /products/{id}:
    get:
      operationId: getProduct
      summary: Get product by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Product details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Product'
```

#### Action Configuration

```json
{
  "action": {
    "id": "getProduct",
    "title": "Get Product Information",
    "description": "Retrieve detailed product information",
    "parameters": {
      "id": {
        "type": "string",
        "description": "Product ID"
      }
    }
  }
}
```

### Custom Engine Agents (C#)

#### Teams Bot Structure

```csharp
using Microsoft.Bot.Builder;
using Microsoft.Bot.Schema;
using Microsoft.Teams.AI;

public class ProductSupportBot : TeamsActivityHandler
{
    private readonly IConfiguration _configuration;
    
    public ProductSupportBot(IConfiguration configuration)
    {
        _configuration = configuration;
    }
    
    protected override async Task OnMessageActivityAsync(
        ITurnContext<IMessageActivity> turnContext,
        CancellationToken cancellationToken)
    {
        var userMessage = turnContext.Activity.Text;
        
        // Process message with your AI logic
        var response = await ProcessMessageAsync(userMessage);
        
        await turnContext.SendActivityAsync(
            MessageFactory.Text(response),
            cancellationToken
        );
    }
}
```

#### AI Configuration

```csharp
using Microsoft.Teams.AI;

public class AIConfig
{
    public static AIOptions CreateAIOptions(IConfiguration configuration)
    {
        return new AIOptions
        {
            Planner = new ActionPlanner(
                new ActionPlannerOptions
                {
                    Model = configuration["OpenAI:Model"],
                    ApiKey = configuration["OpenAI:ApiKey"]
                }
            ),
            PromptManager = new PromptManager("./prompts")
        };
    }
}
```

### Connectors (Node.js/TypeScript)

#### Message Extension

```typescript
import {
  TeamsActivityHandler,
  CardFactory,
  TurnContext,
  MessagingExtensionQuery,
  MessagingExtensionResponse,
} from 'botbuilder';

export class SearchMessageExtension extends TeamsActivityHandler {
  protected async handleTeamsMessagingExtensionQuery(
    context: TurnContext,
    query: MessagingExtensionQuery
  ): Promise<MessagingExtensionResponse> {
    
    const searchQuery = query.parameters[0].value;
    
    // Search your data source
    const results = await this.searchProducts(searchQuery);
    
    // Create adaptive cards for results
    const attachments = results.map(result =>
      CardFactory.adaptiveCard({
        type: 'AdaptiveCard',
        body: [
          {
            type: 'TextBlock',
            text: result.name,
            weight: 'Bolder',
            size: 'Medium'
          },
          {
            type: 'TextBlock',
            text: result.description,
            wrap: true
          }
        ],
        actions: [
          {
            type: 'Action.Submit',
            title: 'Select',
            data: result
          }
        ]
      })
    );
    
    return {
      composeExtension: {
        type: 'result',
        attachmentLayout: 'list',
        attachments: attachments
      }
    };
  }
  
  private async searchProducts(query: string): Promise<any[]> {
    // Implement your search logic
    return [];
  }
}
```

## Microsoft Agents SDK Integration

### C# Integration

#### Copilot Studio Integration

```csharp
using Microsoft.Bot.Connector.DirectLine;
using System.Net.Http;

public class CopilotStudioClient
{
    private readonly DirectLineClient _client;
    private readonly string _conversationId;
    
    public CopilotStudioClient(IConfiguration configuration)
    {
        var secret = configuration["CopilotStudio:DirectLineSecret"];
        _client = new DirectLineClient(secret);
        
        // Start conversation
        var conversation = _client.Conversations.StartConversation();
        _conversationId = conversation.ConversationId;
    }
    
    public async Task<string> SendMessageAsync(string message)
    {
        // Send message
        await _client.Conversations.PostActivityAsync(
            _conversationId,
            new Activity
            {
                Type = ActivityTypes.Message,
                From = new ChannelAccount { Id = "user" },
                Text = message
            }
        );
        
        // Get response
        var activities = await _client.Conversations.GetActivitiesAsync(
            _conversationId
        );
        
        var response = activities.Activities
            .Where(a => a.From.Id != "user")
            .LastOrDefault();
        
        return response?.Text ?? "No response";
    }
}
```

#### Service-to-Service Authentication

```csharp
using Microsoft.Identity.Client;

public class S2SAuthHandler : DelegatingHandler
{
    private readonly IConfiguration _configuration;
    
    public S2SAuthHandler(IConfiguration configuration)
    {
        _configuration = configuration;
    }
    
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var token = await GetAccessTokenAsync();
        request.Headers.Authorization = 
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
        
        return await base.SendAsync(request, cancellationToken);
    }
    
    private async Task<string> GetAccessTokenAsync()
    {
        var app = ConfidentialClientApplicationBuilder
            .Create(_configuration["AzureAd:ClientId"])
            .WithClientSecret(_configuration["AzureAd:ClientSecret"])
            .WithAuthority(_configuration["AzureAd:Authority"])
            .Build();
        
        var result = await app.AcquireTokenForClient(
            new[] { _configuration["AzureAd:Scope"] }
        ).ExecuteAsync();
        
        return result.AccessToken;
    }
}
```

### Azure AI Foundry Agent Integration

#### Calling Agent from Application

```csharp
using Azure.Identity;
using Azure.AI.Projects;

public class AgentIntegration
{
    private readonly AIProjectClient _client;
    private readonly string _agentId;
    
    public AgentIntegration(IConfiguration configuration)
    {
        var endpoint = configuration["AzureAI:ProjectEndpoint"];
        _agentId = configuration["AzureAI:AgentId"];
        
        _client = new AIProjectClient(
            new Uri(endpoint),
            new DefaultAzureCredential()
        );
    }
    
    public async Task<string> ChatWithAgentAsync(
        string threadId,
        string message)
    {
        // Create thread if needed
        if (string.IsNullOrEmpty(threadId))
        {
            var thread = await _client.Agents.Threads.CreateAsync();
            threadId = thread.Id;
        }
        
        // Add message
        await _client.Agents.Messages.CreateAsync(
            threadId,
            role: "user",
            content: message
        );
        
        // Run agent
        var run = await _client.Agents.Runs.CreateAsync(
            threadId,
            _agentId
        );
        
        // Wait for completion
        while (run.Status == "queued" || run.Status == "in_progress")
        {
            await Task.Delay(1000);
            run = await _client.Agents.Runs.RetrieveAsync(threadId, run.Id);
        }
        
        // Get response
        var messages = await _client.Agents.Messages.ListAsync(threadId);
        return messages.Data[0].Content[0].Text.Value;
    }
}
```

### Agent Framework Integration

#### Using Agent in Web Application

```python
from fastapi import FastAPI, WebSocket
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient

app = FastAPI()

@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with agent."""
    await websocket.accept()
    
    async with AzureCliCredential() as credential:
        async with AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        ) as project_client:
            
            async with ChatAgent(
                chat_client=AzureAIAgentClient(
                    project_client=project_client,
                    agent_id=AGENT_ID,
                    async_credential=credential
                )
            ) as agent:
                
                try:
                    while True:
                        # Receive message from client
                        message = await websocket.receive_text()
                        
                        # Stream response from agent
                        async for chunk in agent.send_message_stream(message):
                            await websocket.send_text(chunk.content)
                        
                        # Send end marker
                        await websocket.send_text("[END]")
                        
                except WebSocketDisconnect:
                    print("Client disconnected")
```

## Configuration Management

### C# Configuration

**appsettings.json:**
```json
{
  "AzureAI": {
    "ProjectEndpoint": "https://your-project.services.ai.azure.com/api/projects/your-project",
    "AgentId": "agent-id-here",
    "ModelDeployment": "gpt-4"
  },
  "CopilotStudio": {
    "DirectLineSecret": "",
    "BotId": ""
  },
  "AzureAd": {
    "ClientId": "",
    "ClientSecret": "",
    "TenantId": "",
    "Authority": "https://login.microsoftonline.com/{tenant-id}",
    "Scope": "https://api.example.com/.default"
  },
  "OpenAI": {
    "Model": "gpt-4",
    "ApiKey": ""
  }
}
```

### Python Configuration

**.env:**
```bash
# Azure AI Foundry
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4
AGENT_ID=agent-id-here

# Azure AD
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

## Best Practices

### Security

1. **Never Commit Secrets**: Use configuration files with empty values
2. **Use Managed Identities**: Prefer DefaultAzureCredential
3. **Validate Inputs**: Always validate user inputs before processing
4. **Implement Rate Limiting**: Protect against abuse
5. **Content Filtering**: Use Azure AI Content Safety

### Error Handling

```csharp
try
{
    var response = await agent.ChatAsync(message);
    return response;
}
catch (HttpRequestException ex)
{
    _logger.LogError(ex, "Network error calling agent");
    return "Sorry, I'm having trouble connecting right now.";
}
catch (Exception ex)
{
    _logger.LogError(ex, "Unexpected error");
    return "Sorry, something went wrong.";
}
```

### Testing

```csharp
[Fact]
public async Task Agent_ReturnsValidResponse()
{
    // Arrange
    var agent = new AgentIntegration(_configuration);
    
    // Act
    var response = await agent.ChatWithAgentAsync(null, "Hello");
    
    // Assert
    Assert.NotEmpty(response);
}
```

### Logging and Monitoring

```csharp
using Microsoft.ApplicationInsights;

public class MonitoredAgent
{
    private readonly TelemetryClient _telemetry;
    
    public async Task<string> ProcessAsync(string message)
    {
        using (_telemetry.StartOperation<RequestTelemetry>("AgentRequest"))
        {
            _telemetry.TrackEvent("MessageReceived", new Dictionary<string, string>
            {
                { "MessageLength", message.Length.ToString() }
            });
            
            try
            {
                var response = await CallAgentAsync(message);
                
                _telemetry.TrackMetric("ResponseTime", stopwatch.ElapsedMilliseconds);
                
                return response;
            }
            catch (Exception ex)
            {
                _telemetry.TrackException(ex);
                throw;
            }
        }
    }
}
```

### Performance

1. **Connection Pooling**: Reuse HTTP clients
2. **Async All The Way**: Use async/await consistently
3. **Caching**: Cache frequently accessed data
4. **Batch Operations**: Combine multiple requests when possible
5. **Streaming**: Use streaming for long responses

## Educational Focus

When creating integration examples:

- Show complete, working examples
- Demonstrate authentication patterns
- Include error handling
- Show configuration management
- Provide deployment guidance
- Include monitoring and logging examples
