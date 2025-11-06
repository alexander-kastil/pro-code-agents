using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Agents.AzureAI;
using Microsoft.SemanticKernel.Agents.Chat;
using Microsoft.SemanticKernel.ChatCompletion;
using SKOrchestration;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();
var appConfig = configuration.Get<AppConfig>();

var kernelBuilder = Kernel.CreateBuilder();

kernelBuilder.AddAzureOpenAIChatCompletion(
    appConfig.Model!,
    appConfig.Endpoint!,
    appConfig.ApiKey!);
var kernel = kernelBuilder.Build();

AIProjectClient client = AzureAIAgent.CreateAzureAIClient(appConfig.ProjectConnectionString, new AzureCliCredential());

AgentsClient agentsClient = client.GetAgentsClient();

Azure.AI.Projects.Agent IncidentAgentDefinition = await agentsClient.CreateAgentAsync(
    model: appConfig.Model,
    name: IncidentManager.Name,
    description: IncidentManager.Description,
    instructions: IncidentManager.Instructions);

Azure.AI.Projects.Agent DevOpsAgentDefinition = await agentsClient.CreateAgentAsync(
    model: appConfig.Model,
    name: DevOpsAssistant.Name,
    description: DevOpsAssistant.Description,
    instructions: DevOpsAssistant.Instructions);

AzureAIAgent incidentAgent = new AzureAIAgent(IncidentAgentDefinition, agentsClient, [
    KernelPluginFactory.CreateFromObject(new LogFilePlugin())
]);

AzureAIAgent devOpsAgent = new AzureAIAgent(DevOpsAgentDefinition, agentsClient, [
    KernelPluginFactory.CreateFromObject(new DevopsPlugin())
]);

AgentGroupChat chat = new(incidentAgent, devOpsAgent)
{
    ExecutionSettings = new AgentGroupChatSettings
    {
        SelectionStrategy = new KernelFunctionSelectionStrategy(Selection.selectionFunction, kernel),
        TerminationStrategy = new ApprovalTerminationStrategy()
    }
};

// Get all log files in the "logs" directory
var logDirectory = Path.Combine(Directory.GetCurrentDirectory(), "logs");
foreach (var filePath in Directory.GetFiles(logDirectory))
{
    var fileName = Path.GetFileName(filePath);
    var logFileMsg = new ChatMessageContent(AuthorRole.User, $"USER > {logDirectory}/{fileName}");

    Console.WriteLine($"\nReady to process log file: {fileName}\n");
    // Append the current log file to the chat
    chat.AddChatMessage(logFileMsg);

    try
    {
        Console.WriteLine("Starting chat invocation...");

        // Invoke a response from the agents
        await foreach (var response in chat.InvokeAsync())
        {
            if (response == null || string.IsNullOrEmpty(response.Content))
            {
                Console.WriteLine("No response received.");
                continue;
            }
            Console.WriteLine($"{response.Content}");
        }
        await Task.Delay(1000); // Wait to reduce TPM
    }
    catch (Exception e)
    {
        Console.WriteLine($"Error during chat invocation: {e.Message}");
        // If TPM rate exceeded, wait 60 secs
        if (e.Message.Contains("Rate limit is exceeded"))
        {
            Console.WriteLine("Waiting...");
            await Task.Delay(60000);
            continue;
        }
        else
        {
            break;
        }
    }
}