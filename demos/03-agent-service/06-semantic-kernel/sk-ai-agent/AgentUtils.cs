using Azure.AI.Projects;

namespace sk_ai_agent;

public static class AgentUtils
{
    public static void LogGreen(string message) => Console.WriteLine($"\u001b[32m{message}\u001b[0m");
    public static void LogPurple(string message) => Console.WriteLine($"\u001b[35m{message}\u001b[0m");
    public static void LogBlue(string message) => Console.WriteLine($"\u001b[34m{message}\u001b[0m");
    public static void LogRed(string message) => Console.WriteLine($"\u001b[31m{message}\u001b[0m");

    public static string ReadAgentInstructions(string file)
    {
        var InstructionsFile = Path.Combine("data", file);

        if (!File.Exists(InstructionsFile))
        {
            throw new FileNotFoundException("Instructions file not found.", InstructionsFile);
        }

        string instructions = File.ReadAllText(InstructionsFile);
        return instructions;
    }

    public static async Task<VectorStore> CreateVectorStoreAndUploadKnowledge(AgentsClient agentClient, string filePath)
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

}
