using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using sk_ai_agent;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var appConfig = configuration.Get<AppConfig>();

AIProjectClient client = new AIProjectClient(appConfig.ProjectConnectionString, new AzureCliCredential());

AgentsClient agentsClient = client.GetAgentsClient();

ConnectionsClient cxnClient = client.GetConnectionsClient();
ListConnectionsResponse searchConnections = await cxnClient.GetConnectionsAsync(Azure.AI.Projects.ConnectionType.AzureAISearch);
ConnectionResponse searchConnection = searchConnections.Value[0];

string knowledgeFile = Path.Combine("data", "return-policy.md");
VectorStore store = await AgentUtils.CreateVectorStoreAndUploadKnowledge(agentsClient, knowledgeFile);

// Define an Azure AI agent with file search tool
Agent agent = await agentsClient.CreateAgentAsync(
    model: appConfig.Model,
    name: appConfig.AgentName,
    description: "An agent that uses Azure AI Service",
    instructions: AgentUtils.ReadAgentInstructions("instructions.md"),
    tools: [new Azure.AI.Projects.AzureAISearchToolDefinition()],
    toolResources: new()
    {
        AzureAISearch = new()
        {
            IndexList = { new Azure.AI.Projects.AISearchIndexResource(searchConnection.Id, "manuals-index") }
        },
    });

// Create a thread for the conversation
AgentThread agentThread = await agentsClient.CreateThreadAsync();

try
{
    // Create a user message
    ThreadMessage message = await agentsClient.CreateMessageAsync(
        threadId: agentThread.Id,
        role: MessageRole.User,
        content: "<your user input>"
    );
    
    // Create and process the run
    ThreadRun run = await agentsClient.CreateRunAsync(
        threadId: agentThread.Id,
        assistantId: agent.Id
    );
    
    // Poll until the run completes
    while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress)
    {
        await Task.Delay(1000);
        run = await agentsClient.GetRunAsync(agentThread.Id, run.Id);
    }
    
    if (run.Status == RunStatus.Failed)
    {
        Console.WriteLine($"Run failed: {run.LastError}");
    }
    else
    {
        // Get the messages
        PageableList<ThreadMessage> messages = await agentsClient.GetMessagesAsync(agentThread.Id);
        
        // Display the assistant's responses
        foreach (ThreadMessage msg in messages.Data)
        {
            if (msg.Role == MessageRole.Assistant)
            {
                foreach (MessageContent contentItem in msg.ContentItems)
                {
                    if (contentItem is MessageTextContent textContent)
                    {
                        Console.WriteLine(textContent.Text);
                    }
                }
            }
        }
    }
}
finally
{
    await agentsClient.DeleteThreadAsync(agentThread.Id);
    await agentsClient.DeleteAgentAsync(agent.Id);
}