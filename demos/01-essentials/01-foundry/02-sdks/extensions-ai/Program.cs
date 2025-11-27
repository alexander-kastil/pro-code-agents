using Microsoft.Extensions.Configuration;

IConfiguration configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .Build();

var model = configuration["Model"];
var endpoint = configuration["AzureOpenAIEndpoint"];
var modelRouter = configuration["ModelRouter"];
var systemPrompt = configuration["SystemPrompt"] ?? "You are a helpful assistant.";

var maxHistoryTurns = 12;
if (!string.IsNullOrEmpty(configuration["MaxHistoryTurns"]))
    int.TryParse(configuration["MaxHistoryTurns"], out maxHistoryTurns);

var maxOutputTokens = 10000;
if (!string.IsNullOrEmpty(configuration["MaxOutputTokens"]))
    int.TryParse(configuration["MaxOutputTokens"], out maxOutputTokens);

var temperature = 0.7f;
if (!string.IsNullOrEmpty(configuration["Temperature"]))
    float.TryParse(configuration["Temperature"], out temperature);

var topP = 0.95f;
if (!string.IsNullOrEmpty(configuration["TopP"]))
    float.TryParse(configuration["TopP"], out topP);

var frequencyPenalty = 0.0f;
if (!string.IsNullOrEmpty(configuration["FrequencyPenalty"]))
    float.TryParse(configuration["FrequencyPenalty"], out frequencyPenalty);

var presencePenalty = 0.0f;
if (!string.IsNullOrEmpty(configuration["PresencePenalty"]))
    float.TryParse(configuration["PresencePenalty"], out presencePenalty);

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