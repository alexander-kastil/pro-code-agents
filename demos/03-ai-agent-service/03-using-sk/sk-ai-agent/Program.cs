using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel.Agents.AzureAI;
using sk_ai_agent;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var appConfig = configuration.Get<AppConfig>();


AIProjectClient client = AzureAIAgent.CreateAzureAIClient(appConfig.ProjectConnectionString, new AzureCliCredential());

AgentsClient agentsClient = client.GetAgentsClient();

// 1. Define an agent on the Azure AI agent service
Azure.AI.Projects.Agent definition = await agentsClient.CreateAgentAsync(
    appConfig.Model,
    name: appConfig.AgentName,
    description: "An agent that uses Semantic Kernel and Azure AI Service",
    instructions: AgentUtils.ReadAgentInstructions("instructions.md")
    );

// 2. Create a Semantic Kernel agent based on the agent definition
AzureAIAgent agent = new(definition, agentsClient);