using Azure.AI.Agents.Persistent;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using System.Text;

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
var createMermaidDiagram = configuration.GetValue<bool>("CreateMermaidDiagram", false);
var ticketFolderPath = configuration["TicketFolderPath"] ?? "./tickets";

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

        // Capture the assistant's final response as resolution
        var resolutionBuilder = new StringBuilder();

        await foreach (var msg in messages)
        {
            if (msg.ContentItems.Count > 0)
            {
                foreach (var content in msg.ContentItems)
                {
                    if (content is MessageTextContent textContent)
                    {
                        Console.WriteLine($"Message ({msg.Role}): {textContent.Text.Trim()}\n");
                        // Capture resolution from the last non-User message (agent response)
                        if (msg.Role != MessageRole.User)
                        {
                            resolutionBuilder.Clear();
                            resolutionBuilder.Append(textContent.Text.Trim());
                        }
                    }
                }
            }
        }

        var resolution = resolutionBuilder.ToString();

        // Optionally generate Mermaid diagram file similar to Python demo
        if (createMermaidDiagram)
        {
            try
            {
                Console.WriteLine("Generating Mermaid diagram file...");
                var filePath = DiagramHelper.SaveDiagramFile(
                    ticketFolderPath: ticketFolderPath,
                    ticketPrompt: prompt,
                    resolution: string.IsNullOrWhiteSpace(resolution) ? "Pending" : resolution,
                    tokenUsageIn: 0,
                    tokenUsageOut: 0
                );
                Console.WriteLine($"Diagram file saved: {filePath}\n");
            }
            catch (Exception genEx)
            {
                Console.WriteLine($"Failed to generate diagram file: {genEx.Message}");
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

// Helper class for Mermaid diagram generation and saving
internal static class DiagramHelper
{
    internal static string GenerateDiagram(bool verbose)
    {
        if (verbose)
        {
            return @"sequenceDiagram
    participant User
    participant TriageAgent as Triage Agent<br/>(Main Orchestrator)
    participant PriorityAgent as Priority Agent<br/>(Urgency Assessment)
    participant TeamAgent as Team Agent<br/>(Team Assignment)
    participant EffortAgent as Effort Agent<br/>(Complexity Estimation)

    User->>TriageAgent: Submit ticket description
    Note over TriageAgent: Parse ticket content<br/>Identify key requirements<br/>Plan assessment strategy

    TriageAgent->>PriorityAgent: Request priority assessment
    Note over PriorityAgent: Analyze ticket urgency:<br/>• User-facing/blocking → High<br/>• Time-sensitive → Medium<br/>• Cosmetic/non-urgent → Low
    PriorityAgent-->>TriageAgent: Return: Priority level + rationale

    TriageAgent->>TeamAgent: Request team assignment
    Note over TeamAgent: Match ticket to team:<br/>• Frontend (UI/UX issues)<br/>• Backend (API/server logic)<br/>• Infrastructure (deployment/ops)<br/>• Marketing (content/campaigns)
    TeamAgent-->>TriageAgent: Return: Team name + rationale

    TriageAgent->>EffortAgent: Request effort estimation
    Note over EffortAgent: Estimate work complexity:<br/>• Small: <1 day<br/>• Medium: 2-3 days<br/>• Large: Multi-day/cross-team
    EffortAgent-->>TriageAgent: Return: Effort level + justification

    Note over TriageAgent: Synthesize all assessments<br/>Generate comprehensive triage report
    TriageAgent-->>User: Complete triage analysis<br/>(Priority + Team + Effort)";
        }
        else
        {
            return @"sequenceDiagram
    participant User
    participant TriageAgent
    participant PriorityAgent
    participant TeamAgent
    participant EffortAgent

    User->>TriageAgent: Submit ticket
    TriageAgent->>PriorityAgent: Assess priority
    PriorityAgent-->>TriageAgent: Return priority level
    TriageAgent->>TeamAgent: Determine team
    TeamAgent-->>TriageAgent: Return team assignment
    TriageAgent->>EffortAgent: Estimate effort
    EffortAgent-->>TriageAgent: Return effort estimate
    TriageAgent-->>User: Complete triage analysis";
        }
    }

    internal static string SaveDiagramFile(string ticketFolderPath, string ticketPrompt, string resolution, int tokenUsageIn, int tokenUsageOut)
    {
        var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
        var ticketId = timestamp;

        var simpleDiagram = GenerateDiagram(verbose: false);
        var verboseDiagram = GenerateDiagram(verbose: true);

        var tokenUsageTotal = tokenUsageIn + tokenUsageOut;

        var sb = new StringBuilder();
        sb.AppendLine($"# Ticket {ticketId}");
        sb.AppendLine();
        sb.AppendLine("## Ticket Description");
        sb.AppendLine($"- **Description**: {ticketPrompt}");
        sb.AppendLine($"- **Resolution**: {resolution}");
        sb.AppendLine($"- **Token Usage**: In: {tokenUsageIn}, Out: {tokenUsageOut}, Total: {tokenUsageTotal}");
        sb.AppendLine();
        sb.AppendLine("## Diagram");
        sb.AppendLine("```mermaid");
        sb.AppendLine(simpleDiagram);
        sb.AppendLine("```");
        sb.AppendLine();
        sb.AppendLine("## Verbose Diagram");
        sb.AppendLine("```mermaid");
        sb.AppendLine(verboseDiagram);
        sb.AppendLine("```");

        Directory.CreateDirectory(ticketFolderPath);
        var filePath = Path.Combine(ticketFolderPath, $"ticket-{ticketId}.md");
        File.WriteAllText(filePath, sb.ToString());
        return Path.GetFullPath(filePath);
    }
}
