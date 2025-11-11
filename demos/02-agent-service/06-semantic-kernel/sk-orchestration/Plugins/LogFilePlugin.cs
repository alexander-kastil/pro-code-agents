using Azure.AI.Agents.Persistent;
using System.Text.Json;

namespace SKOrchestration;

public static class LogFilePlugin
{
    public static string ReadLogFile(string filepath = "")
    {
        var originalLog = File.ReadAllText(filepath);
        var progressLogPath = filepath.Replace(".log", "-progress.log");

        // Check if progress log exists and append it
        if (File.Exists(progressLogPath))
        {
            var progressLog = File.ReadAllText(progressLogPath);
            return $"{originalLog}\n\n--- ACTIONS IN PROGRESS ---\n{progressLog}";
        }

        return originalLog;
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
