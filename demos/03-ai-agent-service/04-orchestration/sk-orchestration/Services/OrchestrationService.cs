using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.Extensions.Logging;

namespace SKOrchestration
{
    public class OrchestrationService
    {
        private readonly IConfiguration configuration;
        private readonly ILogger<OrchestrationService> logger;
        private const int DelaySeconds = 15;
        private const string LogSourcePath = "sample_logs";
        private const string LogDestPath = "logs";

        public OrchestrationService(IConfiguration configuration, ILogger<OrchestrationService> logger)
        {
            this.configuration = configuration;
            this.logger = logger;
        }

        private const string IncidentManager = "INCIDENT_MANAGER";
        private const string IncidentManagerInstructions = @"
Analyze the given log file or the response from the devops assistant.
Recommend which one of the following actions should be taken:

Restart service {service_name}
Rollback transaction
Redeploy resource {resource_name}
Increase quota

If there are no issues or if the issue has already been resolved, respond with ""INCIDENT_MANAGER > No action needed.""
If none of the options resolve the issue, respond with ""Escalate issue.""

RULES:
- Do not perform any corrective actions yourself.
- Read the log file on every turn.
- Prepend your response with this text: ""INCIDENT_MANAGER > {logfilepath} | ""
- Only respond with the corrective action instructions.
";

        private const string DevopsAssistant = "DEVOPS_ASSISTANT";
        private const string DevopsAssistantInstructions = @"
Read the instructions from the INCIDENT_MANAGER and apply the appropriate resolution function. 
Return the response as ""{function_response}""
If the instructions indicate there are no issues or actions needed, 
take no action and respond with ""No action needed.""

RULES:
- Use the instructions provided.
- Do not read any log files yourself.
- Prepend your response with this text: ""DEVOPS_ASSISTANT > ""
";

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            // Clear the console
            Console.Clear();

            // Get the log files
            Console.WriteLine("Getting log files...\n");
            await ProcessLogFiles(stoppingToken);

            // Signal completion
            Console.WriteLine("\nProcessing complete.");
        }

        private async Task ProcessLogFiles(CancellationToken cancellationToken)
        {
            const int delay = 15;

            // Setup file paths
            var scriptDir = AppDomain.CurrentDomain.BaseDirectory;
            var srcPath = Path.Combine(scriptDir, LogSourcePath);
            var filePath = Path.Combine(scriptDir, LogDestPath);

            // Ensure logs directory exists and copy sample logs
            await LogService.CopyLogFilesAsync(srcPath, filePath);

            // Setup agents and chat
            var (chat, client) = await SetupAgentsAndChat(cancellationToken);
            using (client) // Ensure proper disposal of the client
            {
                // Process log files
                foreach (var file in Directory.GetFiles(filePath))
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    var filename = Path.GetFileName(file);
                    Console.WriteLine($"\nReady to process log file: {filename}\n");

                    // Create a user message with the log file path
                    var logfileMsg = new ChatMessageContent(
                        AuthorRole.User,
                        $"USER > {file}"
                    );

                    // Append the current log file to the chat
                    await chat.AddMessageAsync(logfileMsg, cancellationToken);
                    Console.WriteLine();

                    try
                    {
                        Console.WriteLine();

                        // Invoke a response from the agents
                        await foreach (var response in chat.InvokeAsync(cancellationToken))
                        {
                            if (string.IsNullOrEmpty(response.Name))
                                continue;

                            Console.WriteLine($"{response.Content}");
                        }

                        // Wait to reduce TPM
                        await Task.Delay(TimeSpan.FromSeconds(delay), cancellationToken);
                    }
                    catch (Exception e)
                    {
                        logger.LogError(e, "Error during chat invocation");
                        Console.WriteLine($"Error during chat invocation: {e}");

                        // If TPM rate exceeded, wait 60 secs
                        if (e.Message.Contains("Rate limit is exceeded"))
                        {
                            Console.WriteLine("Waiting...");
                            await Task.Delay(TimeSpan.FromSeconds(60), cancellationToken);
                            continue;
                        }
                        else
                        {
                            break;
                        }
                    }
                }
            }
        }

        private async Task<(AgentGroupChat Chat, AzureOpenAIAgentClient Client)> SetupAgentsAndChat(CancellationToken cancellationToken)
        {
            var modelDeployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ??
                                 configuration["AZURE_OPENAI_DEPLOYMENT_NAME"];

            var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT") ??
                          configuration["AZURE_OPENAI_ENDPOINT"];

            // Setup Azure AI Agent client
            var credential = new DefaultAzureCredential(new DefaultAzureCredentialOptions
            {
                ExcludeEnvironmentCredential = true,
                ExcludeManagedIdentityCredential = true
            });

            var clientOptions = new AzureOpenAIAgentClientOptions
            {
                Endpoint = new Uri(endpoint)
            };

            var client = new AzureOpenAIAgentClient(modelDeployment, credential, clientOptions);

            // Create the incident manager agent
            var incidentAgentDefinition = await client.CreateAgentAsync(
                modelDeployment,
                IncidentManager,
                IncidentManagerInstructions,
                cancellationToken);

            // Create a Semantic Kernel agent for the incident manager
            var logFilePlugin = new LogFilePlugin();
            var kernel = Kernel.CreateBuilder().Build();
            kernel.ImportPluginFromObject(logFilePlugin);

            var agentIncident = new AzureOpenAIAgent(
                client,
                incidentAgentDefinition,
                kernel);

            // Create the devops agent
            var devopsAgentDefinition = await client.CreateAgentAsync(
                modelDeployment,
                DevopsAssistant,
                DevopsAssistantInstructions,
                cancellationToken);

            // Create a Semantic Kernel agent for the devops agent
            var devopsPlugin = new DevopsPlugin();
            var devopsKernel = Kernel.CreateBuilder().Build();
            devopsKernel.ImportPluginFromObject(devopsPlugin);

            var agentDevops = new AzureOpenAIAgent(
                client,
                devopsAgentDefinition,
                devopsKernel);

            // Add the agents to a group chat with custom strategies
            var agents = new List<IAgent> { agentIncident, agentDevops };

            var chat = new AgentGroupChat(
                agents,
                new ApprovalTerminationStrategy(
                    approvalAgents: new List<IAgent> { agentIncident },
                    maximumIterations: 5,
                    automaticReset: true
                ),
                new SelectionStrategy(agents)
            );

            return (chat, client);
        }
    }
}
