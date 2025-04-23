using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.ChatCompletion;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var model = configuration["SemanticKernel:Model"];
var endpoint = configuration["SemanticKernel:Endpoint"];
var resourceKey = configuration["SemanticKernel:ApiKey"];

Console.WriteLine("Hello Welcome to Semantic Kernel School");

var kernelBuilder = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(model, endpoint, resourceKey).Build();

// Define the agents
var mathsAgent = Agents.CreateMathsAgent(kernelBuilder);

var englishAgent = Agents.CreateEnglishAgent(kernelBuilder);

var principalAgent = Agents.CreatePrincipalAgent(kernelBuilder);

AgentGroupChat chat = Agents.GetGroupChat([principalAgent, englishAgent, mathsAgent]);

//// Invoke chat and display messages.
var initialPrompt = "Please provide the sum of 12 and 13";
Console.ForegroundColor = ConsoleColor.Yellow;
Console.WriteLine($"# User: '{initialPrompt}'");

chat.AddChatMessage(new ChatMessageContent(AuthorRole.User, "Semantic kernel is a powerful tool for natural language processing, enabling more accurate understanding of context and meaning."));
chat.AddChatMessage(new ChatMessageContent(AuthorRole.User, initialPrompt));

await foreach (var content in chat.InvokeAsync())
{
    Console.ForegroundColor = ConsoleColor.White;
    Console.WriteLine("\n");

    Console.ForegroundColor = content.AuthorName switch
    {
        "Principal" => ConsoleColor.Red,
        "EnglishTeacher" => ConsoleColor.Blue,
        "MathsTeacher" => ConsoleColor.Green,
        _ => Console.ForegroundColor
    };

    Console.WriteLine($"# {content.Role} - {content.AuthorName ?? "*"}: '{content.Content}'");
}

Console.WriteLine($"# IS COMPLETE: {chat.IsComplete}");

Console.Read();