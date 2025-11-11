using Azure.AI.Projects;
using System.Text.Json;

namespace SKOrchestration;

public static class LogFilePlugin
{
    public static string ReadLogFile(string filepath = "")
    {
        return File.ReadAllText(filepath);
    }

    public static FunctionToolDefinition GetToolDefinition()
    {
        return new FunctionToolDefinition(
            name: nameof(ReadLogFile),
            description: "Accesses the given file path string and returns the file contents as a string",
            parameters: BinaryData.FromObjectAsJson(new
            {
                Type = "object",
                Properties = new
                {
                    Filepath = new
                    {
                        Type = "string",
                        Description = "The path to the log file to read"
                    }
                },
                Required = new[] { "filepath" }
            },
            new JsonSerializerOptions() { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })
        );
    }
}