using Azure.AI.Projects;

namespace SalesAgentApp;

public static class AgentUtils
{
    public static void LogGreen(string message) => Console.WriteLine($"\u001b[32m{message}\u001b[0m");
    public static void LogPurple(string message) => Console.WriteLine($"\u001b[35m{message}\u001b[0m");
    public static void LogBlue(string message) => Console.WriteLine($"\u001b[34m{message}\u001b[0m");
    public static void LogRed(string message) => Console.WriteLine($"\u001b[31m{message}\u001b[0m");
}
