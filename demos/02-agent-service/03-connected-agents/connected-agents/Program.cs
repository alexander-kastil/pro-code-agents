using Azure.AI.Agents;
using Azure.AI.Agents.Models;
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

// Agent instructions
var priorityAgentInstructions = """
Assess how urgent a ticket is based on its description.

Respond with one of the following levels:
- High: User-facing or blocking issues
- Medium: Time-sensitive but not breaking anything
- Low: Cosmetic or non-urgent tasks

Only output the urgency level and a very brief explanation.
""";

var teamAgentInstructions = """
Decide which team should own each ticket.

Choose from the following teams:
- Frontend
- Backend
- Infrastructure
- Marketing

Base your answer on the content of the ticket. Respond with the team name and a very brief explanation.
""";

var effortAgentInstructions = """
Estimate how much work each ticket will require.

Use the following scale:
- Small: Can be completed in a day
- Medium: 2-3 days of work
- Large: Multi-day or cross-team effort

Base your estimate on the complexity implied by the ticket. Respond with the effort level and a brief justification.
""";

var triageAgentInstructions = """
Triage the given ticket. Use the connected tools to determine the ticket's priority, 
which team it should be assigned to, and how much effort it may take.
""";

// Create the agents client
Console.WriteLine("Initializing AgentsClient...");
var agentsClient = new AgentsClient(
    projectConnectionString,
    new DefaultAzureCredential(new DefaultAzureCredentialOptions
    {
        ExcludeEnvironmentCredential = true,
        ExcludeManagedIdentityCredential = true
    })
);
Console.WriteLine("AgentsClient initialized.\n");

try
{
    // Create the priority agent
    Console.WriteLine("Creating priority agent...");
    var priorityAgent = await agentsClient.CreateAgentAsync(
        model: model,
        name: "priority_agent",
        instructions: priorityAgentInstructions
    );
    Console.WriteLine($"Priority agent created: id={priorityAgent.Value.Id}");

    // Create connected agent tool for priority agent
    var priorityAgentTool = new ConnectedAgentTool(
        agentId: priorityAgent.Value.Id,
        name: "priority_agent",
        description: "Assess the priority of a ticket"
    );

    // Create the team agent
    Console.WriteLine("Creating team agent...");
    var teamAgent = await agentsClient.CreateAgentAsync(
        model: model,
        name: "connected_supervisor_agent",
        instructions: teamAgentInstructions
    );
    Console.WriteLine($"Team agent created: id={teamAgent.Value.Id}");

    // Create connected agent tool for team agent
    var teamAgentTool = new ConnectedAgentTool(
        agentId: teamAgent.Value.Id,
        name: "connected_supervisor_agent",
        description: "Determines which team should take the ticket"
    );

    // Create the effort agent
    Console.WriteLine("Creating effort agent...");
    var effortAgent = await agentsClient.CreateAgentAsync(
        model: model,
        name: "effort_agent",
        instructions: effortAgentInstructions
    );
    Console.WriteLine($"Effort agent created: id={effortAgent.Value.Id}");

    // Create connected agent tool for effort agent
    var effortAgentTool = new ConnectedAgentTool(
        agentId: effortAgent.Value.Id,
        name: "effort_agent",
        description: "Determines the effort required to complete the ticket"
    );

    // Create the main triage agent with connected tools
    Console.WriteLine("Creating triage agent with connected tools...");
    var triageAgent = await agentsClient.CreateAgentAsync(
        model: model,
        name: "triage-agent",
        instructions: triageAgentInstructions,
        tools: new List<ToolDefinition>
        {
            priorityAgentTool.Definition,
            teamAgentTool.Definition,
            effortAgentTool.Definition
        }
    );
    Console.WriteLine($"Triage agent created: id={triageAgent.Value.Id}\n");

    // Create thread for the chat session
    Console.WriteLine("Creating a new thread for the triage session...");
    var thread = await agentsClient.CreateThreadAsync();
    Console.WriteLine($"Thread created: id={thread.Value.Id}\n");

    // Create the ticket prompt
    var prompt = "Users can't reset their password from the mobile app.";
    Console.WriteLine($"Prompt prepared: {prompt}\n");

    // Send a prompt to the agent
    Console.WriteLine("Sending user message to thread...");
    var message = await agentsClient.CreateMessageAsync(
        threadId: thread.Value.Id,
        role: MessageRole.User,
        content: prompt
    );
    Console.WriteLine($"Message sent: id={message.Value.Id}, role={message.Value.Role}\n");

    // Create and process the run
    Console.WriteLine("Starting run (create and process)...");
    var run = await agentsClient.CreateAndProcessRunAsync(
        threadId: thread.Value.Id,
        agentId: triageAgent.Value.Id
    );
    Console.WriteLine($"Run finished: id={run.Value.Id}, status={run.Value.Status}\n");

    if (run.Value.Status == RunStatus.Failed)
    {
        Console.WriteLine($"Run failed: {run.Value.LastError?.Message}");
    }
    else
    {
        Console.WriteLine("Run succeeded. Collecting messages...\n");

        // Fetch and display all messages
        var messages = agentsClient.GetMessagesAsync(
            threadId: thread.Value.Id,
            order: ListSortOrder.Ascending
        );

        await foreach (var msg in messages)
        {
            if (msg.ContentItems.Count > 0)
            {
                var lastContent = msg.ContentItems.Last();
                if (lastContent is MessageTextContent textContent)
                {
                    Console.WriteLine($"Message ({msg.Role}): {textContent.Text.Trim()}");
                }
            }
        }
    }

    // Clean up agents
    Console.WriteLine("\nCleaning up agents...");
    await agentsClient.DeleteAgentAsync(triageAgent.Value.Id);
    Console.WriteLine("Deleted triage agent.");
    await agentsClient.DeleteAgentAsync(priorityAgent.Value.Id);
    Console.WriteLine("Deleted priority agent.");
    await agentsClient.DeleteAgentAsync(teamAgent.Value.Id);
    Console.WriteLine("Deleted team agent.");
    await agentsClient.DeleteAgentAsync(effortAgent.Value.Id);
    Console.WriteLine("Deleted effort agent.");
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
    if (verboseOutput)
    {
        Console.WriteLine($"Stack trace: {ex.StackTrace}");
    }
}
