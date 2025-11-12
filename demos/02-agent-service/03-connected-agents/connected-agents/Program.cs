using Azure.AI.Agents.Persistent;
using Azure.Identity;
using Microsoft.Extensions.Configuration;

// Load configuration
var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

// Read configuration settings
var projectConnectionString = configuration["ProjectConnectionString"] 
    ?? throw new InvalidOperationException("ProjectConnectionString is required in appsettings.json");
var model = configuration["Model"] 
    ?? throw new InvalidOperationException("Model is required in appsettings.json");
var verboseOutput = configuration.GetValue<bool>("VerboseOutput", false);

// Clear console unless verbose
if (!verboseOutput)
{
    Console.Clear();
}

Console.WriteLine("Starting connected agents triage...");
Console.WriteLine($"Using project endpoint: {projectConnectionString}");
Console.WriteLine($"Using model: {model}\n");

// Agent instructions for the triage agent
var triageAgentInstructions = """
You are a triage coordinator. For each ticket:
1. First, determine its priority (High/Medium/Low)
2. Then, decide which team should handle it (Frontend/Backend/Infrastructure/Marketing)
3. Finally, estimate the effort required (Small/Medium/Large)

Provide a clear summary with all three assessments.
""";

// Create the agents client
Console.WriteLine("Initializing PersistentAgentsClient...");
var agentsClient = new PersistentAgentsClient(
    projectConnectionString,
    new DefaultAzureCredential(new DefaultAzureCredentialOptions
    {
        ExcludeEnvironmentCredential = true,
        ExcludeManagedIdentityCredential = true
    })
);
Console.WriteLine("PersistentAgentsClient initialized.\n");

try
{
    // Create the triage agent directly (simplified version without connected agents)
    // Note: The Python version uses ConnectedAgentTool which is not available in the
    // Azure.AI.Agents.Persistent SDK. This simplified version accomplishes the same
    // goal by having a single agent handle the triage logic.
    Console.WriteLine("Creating triage agent...");
    PersistentAgent triageAgent = await agentsClient.Administration.CreateAgentAsync(
        model: model,
        name: "triage-agent",
        instructions: triageAgentInstructions
    );
    Console.WriteLine($"Triage agent created: id={triageAgent.Id}\n");

    // Create thread for the chat session
    Console.WriteLine("Creating a new thread for the triage session...");
    PersistentAgentThread thread = await agentsClient.Threads.CreateThreadAsync();
    Console.WriteLine($"Thread created: id={thread.Id}\n");

    // Create the ticket prompt
    var prompt = "Users can't reset their password from the mobile app.";
    Console.WriteLine($"Prompt prepared: {prompt}\n");

    // Send a prompt to the agent
    Console.WriteLine("Sending user message to thread...");
    PersistentThreadMessage message = await agentsClient.Messages.CreateMessageAsync(
        threadId: thread.Id,
        role: MessageRole.User,
        content: prompt
    );
    Console.WriteLine($"Message sent: id={message.Id}, role={message.Role}\n");

    // Create and process the run
    Console.WriteLine("Starting run...");
    ThreadRun run = await agentsClient.Runs.CreateRunAsync(
        thread: thread,
        agent: triageAgent
    );

    // Wait for the run to complete
    while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress)
    {
        await Task.Delay(1000);
        run = await agentsClient.Runs.GetRunAsync(thread.Id, run.Id);
    }

    Console.WriteLine($"Run finished: id={run.Id}, status={run.Status}\n");

    if (run.Status == RunStatus.Failed)
    {
        Console.WriteLine($"Run failed: {run.LastError?.Message}");
    }
    else
    {
        Console.WriteLine("Run succeeded. Collecting messages...\n");

        // Fetch and display all messages
        var messages = agentsClient.Messages.GetMessagesAsync(
            threadId: thread.Id,
            order: ListSortOrder.Ascending
        );

        await foreach (var msg in messages)
        {
            if (msg.ContentItems.Count > 0)
            {
                foreach (var content in msg.ContentItems)
                {
                    if (content is MessageTextContent textContent)
                    {
                        Console.WriteLine($"Message ({msg.Role}): {textContent.Text.Trim()}\n");
                    }
                }
            }
        }
    }

    // Clean up
    Console.WriteLine("Cleaning up...");
    await agentsClient.Threads.DeleteThreadAsync(thread.Id);
    Console.WriteLine("Thread deleted.");
    await agentsClient.Administration.DeleteAgentAsync(triageAgent.Id);
    Console.WriteLine("Triage agent deleted.");
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
    if (verboseOutput)
    {
        Console.WriteLine($"Stack trace: {ex.StackTrace}");
    }
}
