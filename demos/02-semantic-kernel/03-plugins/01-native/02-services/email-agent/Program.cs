// filepath: d:\git-classes\agents-copilots\demos\02-semantic-kernel\02-plugins\02-services\email-agent\Program.cs
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.AzureOpenAI;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using EmailAgent.Common;
using EmailAgent.Plugins;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

// Get the strongly typed configuration
var appConfig = configuration.Get<AppConfig>();

var model = appConfig.SemanticKernel.Model;
var endpoint = appConfig.SemanticKernel.Endpoint;
var resourceKey = appConfig.SemanticKernel.ApiKey;

// Create kernel with an email plugin
var skBuilder = Kernel.CreateBuilder();
// Add services to the kernel
skBuilder.Services.AddSingleton(appConfig.GraphCfg);

// Create and add email plugin
var emailPlugin = new EmailPlugin(appConfig.GraphCfg);
skBuilder.Plugins.AddFromObject(emailPlugin);
Kernel kernel = skBuilder.Build();

skBuilder.Services.AddAzureOpenAIChatCompletion(
    model,
    endpoint,
    resourceKey
);

AzureOpenAIChatCompletionService chatCompletionService = new(
    deploymentName: model,
    apiKey: resourceKey,
    endpoint: endpoint
);

// Create chat history
var history = new ChatHistory("""
    You are a friendly assistant who likes to follow the rules. You will complete required steps
    and request approval before taking any consequential actions. If the user doesn't provide
    enough information for you to complete a task, you will keep asking questions until you have
    enough information to complete the task.
    """);

// Start the conversation
while (true)
{
    // Get user input
    Console.Write("How can I help you?: ");
    var prompt = Console.ReadLine();
    history.AddUserMessage(prompt);

    // Get the chat completions
    OpenAIPromptExecutionSettings openAIPromptExecutionSettings = new()
    {
        ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
    };

    var result = chatCompletionService.GetStreamingChatMessageContentsAsync(
        history,
        executionSettings: openAIPromptExecutionSettings,
        kernel: kernel);

    // Stream the results
    string fullMessage = "";
    await foreach (var content in result)
    {
        if (content.Role.HasValue)
        {
            Console.Write("");
        }
        Console.Write(content.Content);
        fullMessage += content.Content;
    }
    Console.WriteLine();

    // Add the message from the agent to the chat history
    history.AddAssistantMessage(fullMessage);
}