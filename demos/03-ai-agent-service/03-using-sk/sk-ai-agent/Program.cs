using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents.AzureAI;
using Microsoft.SemanticKernel.ChatCompletion;
using sk_ai_agent;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var appConfig = configuration.Get<AppConfig>();


AIProjectClient client = AzureAIAgent.CreateAzureAIClient(appConfig.ProjectConnectionString, new AzureCliCredential());

AgentsClient agentsClient = client.GetAgentsClient();

ConnectionsClient cxnClient = client.GetConnectionsClient();
ListConnectionsResponse searchConnections = await cxnClient.GetConnectionsAsync(Azure.AI.Projects.ConnectionType.AzureAISearch);
ConnectionResponse searchConnection = searchConnections.Value[0];

// 1. Define an agent on the Azure AI agent service
Azure.AI.Projects.Agent definition = await agentsClient.CreateAgentAsync(
    model: appConfig.Model,
    name: appConfig.AgentName,
    description: "An agent that uses Semantic Kernel and Azure AI Service",
    instructions: AgentUtils.ReadAgentInstructions("instructions.md"),
    tools: [new Azure.AI.Projects.AzureAISearchToolDefinition()],
    toolResources: new()
    {
        AzureAISearch = new()
        {
            IndexList = { new Azure.AI.Projects.AISearchIndexResource(searchConnection.Id, "manuals-index") }
        }
    });

// 2. Create a Semantic Kernel agent based on the agent definition
AzureAIAgent agent = new(definition, agentsClient);

Microsoft.SemanticKernel.Agents.AgentThread agentThread = new AzureAIAgentThread(agent.Client);
try
{
    ChatMessageContent message = new(AuthorRole.User, "<your user input>");
    await foreach (ChatMessageContent response in agent.InvokeAsync(message, agentThread))
    {
        Console.WriteLine(response.Content);
    }
}
finally
{
    await agentThread.DeleteAsync();
    await agent.Client.DeleteAgentAsync(agent.Id);
}