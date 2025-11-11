using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using SKOrchestration;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();
var appConfig = configuration.Get<AppConfig>();

AIProjectClient client = new AIProjectClient(appConfig.ProjectConnectionString, new AzureCliCredential());
AgentsClient agentsClient = client.GetAgentsClient();

// Create the incident manager agent with log file reading capability
Agent incidentAgent = await agentsClient.CreateAgentAsync(
    model: appConfig.Model,
    name: IncidentManager.Name,
    description: IncidentManager.Description,
    instructions: IncidentManager.Instructions,
    tools: new List<ToolDefinition> { LogFilePlugin.GetToolDefinition() }
);

// Create the devops agent with devops operation capabilities
Agent devOpsAgent = await agentsClient.CreateAgentAsync(
    model: appConfig.Model,
    name: DevOpsAssistant.Name,
    description: DevOpsAssistant.Description,
    instructions: DevOpsAssistant.Instructions,
    tools: DevopsPlugin.GetToolDefinitions()
);

// Get all log files in the "logs" directory
var logDirectory = Path.Combine(Directory.GetCurrentDirectory(), "logs");
foreach (var filePath in Directory.GetFiles(logDirectory))
{
    var fileName = Path.GetFileName(filePath);
    Console.WriteLine($"\nProcessing log file: {fileName}\n");

    // Create a new thread for each log file
    AgentThread thread = await agentsClient.CreateThreadAsync();

    try
    {
        int maxIterations = 5;
        int iteration = 0;
        bool resolved = false;

        while (iteration < maxIterations && !resolved)
        {
            iteration++;

            // Create the prompt for this iteration
            string prompt = iteration == 1
                ? $"Analyze this log file and recommend corrective action: {filePath}"
                : $"Check if the issue in {filePath} has been resolved. If not, recommend further action.";

            // Create user message
            await agentsClient.CreateMessageAsync(
                threadId: thread.Id,
                role: MessageRole.User,
                content: prompt
            );

            // Run the incident manager
            ThreadRun incidentRun = await agentsClient.CreateRunAsync(
                threadId: thread.Id,
                assistantId: incidentAgent.Id
            );

            // Process the incident manager's run
            incidentRun = await ProcessRunWithToolCalls(agentsClient, thread.Id, incidentRun);

            if (incidentRun.Status == RunStatus.Failed)
            {
                Console.WriteLine($"Incident manager run failed: {incidentRun.LastError}");
                if (incidentRun.LastError?.Code == "rate_limit_exceeded")
                {
                    Console.WriteLine("Waiting for rate limit...");
                    await Task.Delay(60000);
                    continue;
                }
                break;
            }

            // Get the incident manager's recommendation
            PageableList<ThreadMessage> messages = await agentsClient.GetMessagesAsync(thread.Id);
            ThreadMessage? lastMessage = messages.Data.FirstOrDefault(m => m.Role == MessageRole.Assistant);

            if (lastMessage?.ContentItems.FirstOrDefault() is MessageTextContent textContent)
            {
                string recommendation = textContent.Text;
                Console.WriteLine($"Iteration {iteration} - Incident Manager: {recommendation}\n");

                // Check if resolved
                if (recommendation.Contains("No action needed", StringComparison.OrdinalIgnoreCase))
                {
                    resolved = true;
                    Console.WriteLine($"Issue in {fileName} resolved.\n");
                    break;
                }

                // Create a message for the devops agent
                await agentsClient.CreateMessageAsync(
                    threadId: thread.Id,
                    role: MessageRole.User,
                    content: recommendation
                );

                // Run the devops agent
                ThreadRun devopsRun = await agentsClient.CreateRunAsync(
                    threadId: thread.Id,
                    assistantId: devOpsAgent.Id
                );

                // Process the devops agent's run
                devopsRun = await ProcessRunWithToolCalls(agentsClient, thread.Id, devopsRun);

                if (devopsRun.Status == RunStatus.Failed)
                {
                    Console.WriteLine($"DevOps agent run failed: {devopsRun.LastError}");
                    break;
                }

                // Get the devops agent's response
                messages = await agentsClient.GetMessagesAsync(thread.Id);
                lastMessage = messages.Data.FirstOrDefault(m => m.Role == MessageRole.Assistant);

                if (lastMessage?.ContentItems.FirstOrDefault() is MessageTextContent devopsText)
                {
                    Console.WriteLine($"Iteration {iteration} - DevOps Assistant: {devopsText.Text}\n");
                }
            }

            await Task.Delay(1000); // Wait to reduce TPM
        }

        // Clean up thread
        await agentsClient.DeleteThreadAsync(thread.Id);
    }
    catch (Exception e)
    {
        Console.WriteLine($"Error processing {fileName}: {e.Message}");
        if (e.Message.Contains("Rate limit is exceeded"))
        {
            Console.WriteLine("Waiting...");
            await Task.Delay(60000);
            continue;
        }
    }
}

// Clean up agents
await agentsClient.DeleteAgentAsync(incidentAgent.Id);
await agentsClient.DeleteAgentAsync(devOpsAgent.Id);

// Helper method to process runs with tool calls
static async Task<ThreadRun> ProcessRunWithToolCalls(AgentsClient agentsClient, string threadId, ThreadRun run)
{
    while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress || run.Status == RunStatus.RequiresAction)
    {
        await Task.Delay(1000);
        run = await agentsClient.GetRunAsync(threadId, run.Id);

        if (run.Status == RunStatus.RequiresAction && run.RequiredAction is SubmitToolOutputsAction submitToolOutputsAction)
        {
            var toolOutputs = new List<ToolOutput>();

            foreach (var toolCall in submitToolOutputsAction.ToolCalls)
            {
                if (toolCall is RequiredFunctionToolCall functionToolCall)
                {
                    string result = ToolCallHandler.HandleToolCall(
                        functionToolCall.Name,
                        functionToolCall.Arguments
                    );
                    toolOutputs.Add(new ToolOutput(toolCall.Id, result));
                }
            }

            if (toolOutputs.Any())
            {
                run = await agentsClient.SubmitToolOutputsToRunAsync(threadId, run.Id, toolOutputs);
            }
        }
    }

    return run;
}