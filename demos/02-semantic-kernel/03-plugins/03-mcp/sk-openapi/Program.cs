using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Microsoft.SemanticKernel.Plugins.OpenApi;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var model = configuration["Model"] ?? throw new InvalidOperationException("Model configuration is missing");
var endpoint = configuration["Endpoint"] ?? throw new InvalidOperationException("Endpoint configuration is missing");
var key = configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey configuration is missing");

var kernelBuilder = Kernel.CreateBuilder();

KernelPlugin plugin = await OpenApiKernelPluginFactory.CreateFromOpenApiAsync(
    pluginName: "CurrencyConverter",
    filePath: "data/swagger.json"
);

kernelBuilder.Plugins.Add(plugin);

kernelBuilder.Services.AddAzureOpenAIChatCompletion(
   model,
   endpoint,
   key
);

var kernel = kernelBuilder.Build();

var chatHistory = new ChatHistory("""
    You are a friendly assistant who likes to follow the rules. You will complete required steps
    and request approval before taking any consequential actions. If the user doesn't provide
    enough information for you to complete a task, you will keep asking questions until you have
    enough information to complete the task.
    """);

while (true)
{
    Console.ForegroundColor = ConsoleColor.White;
    Console.WriteLine("\nEnter a prompt (or 'exit' to quit):");
    var prompt = Console.ReadLine();

    if (string.IsNullOrEmpty(prompt) ||
        string.Equals(prompt, "exit", StringComparison.OrdinalIgnoreCase))
    {
        break;
    }

    chatHistory.AddUserMessage(prompt);

    OpenAIPromptExecutionSettings openAIPromptExecutionSettings = new()
    {
        ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
    };

    var chat = kernel.GetRequiredService<IChatCompletionService>();
    var result = chat.GetStreamingChatMessageContentsAsync(
        chatHistory,
        executionSettings: openAIPromptExecutionSettings,
        kernel: kernel);

    Console.ForegroundColor = ConsoleColor.Yellow;
    await foreach (var content in result)
    {
        if (content.Content is not null)
        {
            Console.Write(content.Content);
            chatHistory.AddAssistantMessage(content.Content);
        }
    }
}