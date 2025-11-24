using Microsoft.Extensions.Configuration;

IConfiguration configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .Build();

var model = configuration["Model"];
var endpoint = configuration["AzureOpenAIEndpoint"];
var modelRouter = configuration["ModelRouter"];
var systemPrompt = configuration["SystemPrompt"] ?? "You are a helpful assistant.";
var maxHistoryTurns = int.Parse(configuration["MaxHistoryTurns"] ?? "12");
var maxOutputTokens = int.Parse(configuration["MaxOutputTokens"] ?? "10000");
var temperature = float.Parse(configuration["Temperature"] ?? "0.7");
var topP = float.Parse(configuration["TopP"] ?? "0.95");
var frequencyPenalty = float.Parse(configuration["FrequencyPenalty"] ?? "0.0");
var presencePenalty = float.Parse(configuration["PresencePenalty"] ?? "0.0");

while (true)
{
    Console.WriteLine("\n=== Extensions.AI Demos ===");
    Console.WriteLine("1. ChatRunner - Basic chat using Microsoft.Extensions.AI");
    Console.WriteLine("2. ChatFunctionCalling - Function calling with Microsoft.Extensions.AI");
    Console.WriteLine("3. ChatModelRouterMultiturn - Multi-turn chat with model router");
    Console.WriteLine("\nPress Ctrl+C to exit");
    Console.Write("\nSelect demo (1-3): ");

    var choice = Console.ReadLine();

    try
    {
        switch (choice)
        {
            case "1":
                Console.WriteLine("\n--- Running ChatRunner ---\n");
                ChatRunner chatRunner = new ChatRunner();
                await chatRunner.Run(model, endpoint);
                break;
            case "2":
                Console.WriteLine("\n--- Running ChatFunctionCalling ---\n");
                ChatFunctionCalling functionCalling = new ChatFunctionCalling();
                functionCalling.Run(model, endpoint);
                break;
            case "3":
                Console.WriteLine("\n--- Running ChatModelRouterMultiturn ---\n");
                ChatModelRouterMultiturn modelRouterMultiturn = new ChatModelRouterMultiturn();
                await modelRouterMultiturn.Run(
                    modelRouter, 
                    endpoint, 
                    systemPrompt,
                    maxHistoryTurns,
                    maxOutputTokens,
                    temperature,
                    topP,
                    frequencyPenalty,
                    presencePenalty);
                break;
            default:
                Console.WriteLine("Invalid selection. Please enter 1-3.");
                break;
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error running demo: {ex.Message}");
    }

    Console.WriteLine("\n" + new string('-', 50));
}