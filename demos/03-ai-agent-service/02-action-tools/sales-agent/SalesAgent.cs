using Azure;
using Azure.AI.Projects;
using Azure.Identity;
using System.ClientModel;
using System.Text.Json;

namespace SalesAgentApp;
public class SalesAgent
{
    private readonly AppConfig config;
    private readonly SalesData SalesDB;
    private AgentsClient? agentClient;
    private Agent? agent;
    private readonly AIProjectClient Client;
    private AgentThread? thread;
    private readonly JsonSerializerOptions options = new() { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
    private bool disposeAgent = true;
    record FetchSalesDataArgs(string Query);

    public SalesAgent(AppConfig config, string instructionsFile)
    {
        this.config = config;
        SalesDB = new(config.DBName);
        Client = new AIProjectClient(config.Project_ConnectionString, new DefaultAzureCredential());
        InstructionsFile = instructionsFile;
    }

    private string InstructionsFile { get; }

    private IEnumerable<ToolDefinition> AddTools() => [
        // Add the definition for a function call to the agent that will be used to fetch sales data
        new FunctionToolDefinition(
                name: nameof(SalesDB.FetchSalesDataAsync),
                description: "This function is used to answer user questions about Contoso sales data by executing SQLite queries against the database.",
                parameters: BinaryData.FromObjectAsJson(new {
                    Type = "object",
                    Properties = new {
                        Query = new {
                            Type = "string",
                            Description = "The input should be a well-formed SQLite query to extract information based on the user's question. The query result will be returned as a JSON object."
                        }
                    },
                    Required = new [] { "query" }
                },
                new JsonSerializerOptions() { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })
            ),
        // Add the definition for a file search tool that will be used to search for files in the vector store
        new FileSearchToolDefinition()
    ];

    public async Task RunAsync()
    {
        await Console.Out.WriteLineAsync("Creating agent...");
        agentClient = Client.GetAgentsClient();

        string knowledgeFile = Path.Combine("data", "datasheet", "contoso-tents-datasheet.pdf");
        VectorStore store = await CreateVectorStoreAndUploadKnowledge(agentClient, knowledgeFile);

        IEnumerable<ToolDefinition> tools = AddTools();

        ToolResources? toolResources = InitializeToolResources(store);

        string instructions = await ReadAgentInstructions();

        agent = await agentClient.CreateAgentAsync(
            model: config.Model,
            name: "Constoso Sales AI Agent",
            instructions: instructions,
            tools: tools,
            temperature: (float?)config.ModelParams.Temperature,
            toolResources: toolResources
        );

        await Console.Out.WriteLineAsync($"Agent created with ID: {agent.Id}");

        thread = await agentClient.CreateThreadAsync();

        await Console.Out.WriteLineAsync($"Thread created with ID: {thread.Id}");

        while (true)
        {
            await Console.Out.WriteLineAsync();
            AgentUtils.LogGreen("Enter your query (type 'exit' or 'save' to quit):");
            string? prompt = await Console.In.ReadLineAsync();

            if (prompt is null || prompt.Equals("exit", StringComparison.InvariantCultureIgnoreCase))
            {
                break; // Exit on null (EOF) or "exit" command
            }

            if (prompt.Equals("save", StringComparison.InvariantCultureIgnoreCase))
            {
                AgentUtils.LogGreen($"Saving thread with ID: {thread.Id} for agent ID: {agent.Id}. You can view this in AI Foundry at https://ai.azure.com.");
                disposeAgent = false;
                continue;
            }

            // Create the message and wait for it to complete, we don't need the return value
            await agentClient.CreateMessageAsync(
                threadId: thread.Id,
                role: MessageRole.User,
                content: prompt
            );

            AsyncCollectionResult<StreamingUpdate> streamingUpdate = agentClient.CreateRunStreamingAsync(
                threadId: thread.Id,
                assistantId: agent.Id,
                maxCompletionTokens: config.ModelParams.MaxCompletionTokens,
                maxPromptTokens: config.ModelParams.MaxPromptTokens,
                temperature: (float?)config.ModelParams.Temperature,
                topP: (float?)config.ModelParams.TopP
            );

            await foreach (StreamingUpdate update in streamingUpdate)
            {
                await HandleStreamingUpdate(update);
            }
        }
    }

    // Initialize the tool resources for the agent. 
    // In this case, we are using a file search tool resource, so we need to pass the vector store ID.
    private ToolResources? InitializeToolResources(VectorStore store)
    {
        if (store is null)
        {
            throw new InvalidOperationException("Vector store must be created before initializing tool resources.");
        }

        return new ToolResources
        {
            FileSearch = new FileSearchToolResource([store.Id], null)
        };
    }

    private async Task<string> ReadAgentInstructions()
    {
        if (!File.Exists(InstructionsFile))
        {
            throw new FileNotFoundException("Instructions file not found.", InstructionsFile);
        }

        string instructions = File.ReadAllText(InstructionsFile);
        string databaseSchema = await SalesDB.GetDatabaseInfoAsync();

        instructions = instructions.Replace("{database_schema_string}", databaseSchema);
        return instructions;
    }

    private async Task<VectorStore> CreateVectorStoreAndUploadKnowledge(AgentsClient agentClient, string filePath)
    {
        AgentUtils.LogPurple($"Uploading file: {filePath}");

        AgentFile file = await agentClient.UploadFileAsync(
            filePath: filePath,
            purpose: AgentFilePurpose.Agents
        );

        AgentUtils.LogPurple($"File uploaded: {file.Id}");

        VectorStore vectorStore = await agentClient.CreateVectorStoreAsync(
            fileIds: [file.Id],
            name: "Contoso Product Information Vector Store"
        );

        AgentUtils.LogPurple($"Vector store created: {vectorStore.Id}");
        return vectorStore;
    }

    private async Task HandleStreamingUpdate(StreamingUpdate update)
    {
        switch (update.UpdateKind)
        {
            case StreamingUpdateReason.RunRequiresAction:
                // Print status only for non-content updates
                Console.WriteLine($"\nStreaming Update received: {update.UpdateKind}");
                RequiredActionUpdate requiredActionUpdate = (RequiredActionUpdate)update;
                await HandleRequiredActionAsync(requiredActionUpdate);
                break;

            case StreamingUpdateReason.MessageUpdated:
                // Only print the message content fragment, without the status line
                MessageContentUpdate messageContentUpdate = (MessageContentUpdate)update;
                await Console.Out.WriteAsync(messageContentUpdate.Text); // Keep WriteAsync for continuous text
                break;

            case StreamingUpdateReason.MessageCompleted:
                // Print status only for non-content updates
                Console.WriteLine($"\nStreaming Update received: {update.UpdateKind}");
                MessageStatusUpdate messageStatusUpdate = (MessageStatusUpdate)update;
                ThreadMessage tm = messageStatusUpdate.Value;
                var contentItems = tm.ContentItems;
                foreach (MessageContent contentItem in contentItems)
                {
                    if (contentItem is MessageImageFileContent imageContent)
                    {
                        await DownloadImageFileContentAsync(imageContent);
                    }
                }
                break;

            case StreamingUpdateReason.RunCompleted:
                // Print status only for non-content updates
                Console.WriteLine($"\nStreaming Update received: {update.UpdateKind}");
                // The run is complete, print a final new line to ensure the next prompt starts cleanly.
                await Console.Out.WriteLineAsync();
                break;

            case StreamingUpdateReason.RunFailed:
                // Print status only for non-content updates
                Console.WriteLine($"\nStreaming Update received: {update.UpdateKind}");
                RunUpdate runFailedUpdate = (RunUpdate)update;
                if (runFailedUpdate.Value.LastError.Code == "rate_limit_exceeded")
                {
                    await Console.Out.WriteLineAsync(runFailedUpdate.Value.LastError.Message);
                }
                else
                {
                    await Console.Out.WriteLineAsync($"Error: {runFailedUpdate.Value.LastError.Message} (code: {runFailedUpdate.Value.LastError.Code})");
                }
                break;
        }
    }

    private async Task DownloadImageFileContentAsync(MessageImageFileContent imageContent)
    {
        if (agentClient is null)
        {
            return;
        }

        AgentUtils.LogGreen($"Getting file with ID: {imageContent.FileId}");

        BinaryData fileContent = await agentClient.GetFileContentAsync(imageContent.FileId);
        const string directory = "data";
        if (!Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        string filePath = Path.Combine(directory, imageContent.FileId + ".png");
        await File.WriteAllBytesAsync(filePath, fileContent.ToArray());

        AgentUtils.LogGreen($"File saved to {Path.GetFullPath(filePath)}");
    }

    private AsyncCollectionResult<StreamingUpdate> HandleUnsupportedAction(RequiredActionUpdate requiredActionUpdate)
    {
        throw new NotImplementedException("This function is not implemented in the base SalesAgent class.");
    }

    private async Task HandleRequiredActionAsync(RequiredActionUpdate requiredActionUpdate)
    {
        if (agentClient is null)
        {
            return;
        }

        AsyncCollectionResult<StreamingUpdate> toolOutputUpdate;

        if (requiredActionUpdate.FunctionName == nameof(SalesDB.FetchSalesDataAsync))
        {
            FetchSalesDataArgs salesDataArgs = JsonSerializer.Deserialize<FetchSalesDataArgs>(requiredActionUpdate.FunctionArguments, options) ?? throw new InvalidOperationException("Failed to parse JSON object.");
            string result = await SalesDB.FetchSalesDataAsync(salesDataArgs.Query);
            toolOutputUpdate = agentClient.SubmitToolOutputsToStreamAsync(
            requiredActionUpdate.Value,
            new List<ToolOutput>([new ToolOutput(requiredActionUpdate.ToolCallId, result)])
            );
        }
        else
        {
            toolOutputUpdate = HandleUnsupportedAction(requiredActionUpdate);
        }

        await foreach (StreamingUpdate toolUpdate in toolOutputUpdate)
        {
            await HandleStreamingUpdate(toolUpdate);
        }
    }

    public async ValueTask DisposeAsync()
    {
        SalesDB.Dispose();

        if (!disposeAgent)
        {
            return;
        }

        if (agentClient is not null)
        {
            if (thread is not null)
            {
                await agentClient.DeleteThreadAsync(thread.Id);
            }

            if (agent is not null)
            {
                await agentClient.DeleteAgentAsync(agent.Id);
            }
        }
    }
}
