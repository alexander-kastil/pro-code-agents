using Azure.AI.Agents.Persistent;
using Azure.Identity;
using ConnectedAgents.Models;
using sk_ai_agent;
using System;
using System.IO;
using System.Threading.Tasks;

namespace ConnectedAgentsAI.Services;

public class AiAgentRunner(global::ConnectedAgents.Models.AiAppConfig config)
{
    public async Task RunAsync()
    {
        // Create the Persistent Agents Client
        PersistentAgentsClient client = new PersistentAgentsClient(
            config.ProjectConnectionString,
            new AzureCliCredential());

        string knowledgeFile = Path.Combine("data", "return-policy.md");

        // Upload file and create vector store
        PersistentAgentFileInfo uploadedFile = await client.Files.UploadFileAsync(
            filePath: knowledgeFile,
            purpose: PersistentAgentFilePurpose.Agents);

        AgentUtils.LogPurple($"File uploaded: {uploadedFile.Id}");

        PersistentAgentsVectorStore vectorStore = await client.VectorStores.CreateVectorStoreAsync(
            fileIds: [uploadedFile.Id],
            name: "Contoso Product Information Vector Store");

        AgentUtils.LogPurple($"Vector store created: {vectorStore.Id}");

        // Create file search tool resource
        FileSearchToolResource fileSearchResource = new FileSearchToolResource();
        fileSearchResource.VectorStoreIds.Add(vectorStore.Id);

        // Define an Azure AI agent with file search tool
        PersistentAgent agent = await client.Administration.CreateAgentAsync(
            model: config.Model,
            name: config.AgentName,
            instructions: AgentUtils.ReadAgentInstructions("instructions.md"),
            tools: [new FileSearchToolDefinition()],
            toolResources: new ToolResources { FileSearch = fileSearchResource });

        AgentUtils.LogGreen($"Agent created: {agent.Id}");

        // Create a thread for the conversation
        PersistentAgentThread agentThread = await client.Threads.CreateThreadAsync();

        try
        {
            // Create a user message
            PersistentThreadMessage message = await client.Messages.CreateMessageAsync(
                threadId: agentThread.Id,
                role: MessageRole.User,
                content: "What is the return policy for damaged products?"
            );

            // Create and process the run
            ThreadRun run = await client.Runs.CreateRunAsync(
                thread: agentThread,
                agent: agent
            );

            // Poll until the run completes
            while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress)
            {
                await Task.Delay(1000);
                run = await client.Runs.GetRunAsync(agentThread.Id, run.Id);
            }

            if (run.Status == RunStatus.Failed)
            {
                AgentUtils.LogRed($"Run failed: {run.LastError?.Message}");
            }
            else
            {
                AgentUtils.LogGreen("Run completed successfully!");

                // Get the messages
                var messages = client.Messages.GetMessagesAsync(
                    threadId: agentThread.Id,
                    order: ListSortOrder.Ascending);

                // Display the conversation
                await foreach (PersistentThreadMessage msg in messages)
                {
                    Console.Write($"[{msg.Role}]: ");
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
        finally
        {
            // Cleanup
            await client.Threads.DeleteThreadAsync(agentThread.Id);
            await client.Administration.DeleteAgentAsync(agent.Id);
            await client.VectorStores.DeleteVectorStoreAsync(vectorStore.Id);
            await client.Files.DeleteFileAsync(uploadedFile.Id);
            AgentUtils.LogPurple("Cleanup completed");
        }
    }
}
