using System;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Microsoft.SemanticKernel.Plugins.Core;

#pragma warning disable SKEXP0050 

var builder = new ConfigurationBuilder()
    .AddJsonFile($"appsettings.json", true, true);
IConfigurationRoot configuration = builder.Build();

var model = configuration["SemanticKernel:DeploymentModel"];
var endpoint = configuration["SemanticKernel:Endpoint"];
var key = configuration["SemanticKernel:ApiKey"];

var skBuilder = Kernel.CreateBuilder();
skBuilder.AddAzureOpenAIChatCompletion(
    model,
    endpoint,
    key);

var kernel = skBuilder.Build();

StringBuilder chatHistory = new();

kernel.ImportPluginFromType<CurrencyConverter>();
kernel.ImportPluginFromType<ConversationSummaryPlugin>();
var prompts = kernel.ImportPluginFromPromptDirectory("Prompts");

string input;

do
{
    Console.WriteLine("What would you like to do?");
    input = Console.ReadLine();

    OpenAIPromptExecutionSettings settings = new()
    {
        ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
    };

    var intent = await kernel.InvokeAsync<string>(
        prompts["GetIntent"],
        new() { { "input", input } }
    );

    switch (intent)
    {
        case "ConvertCurrency":
            var currencyText = await kernel.InvokeAsync<string>(
                prompts["GetTargetCurrencies"],
                new() { { "input", input } }
            );
            var currencyInfo = currencyText!.Split("|");
            var result = await kernel.InvokeAsync("CurrencyConverter",
                "ConvertAmount",
                new() {
                {"targetCurrencyCode", currencyInfo[0]},
                {"baseCurrencyCode", currencyInfo[1]},
                {"amount", currencyInfo[2]},
                }
            );
            Console.WriteLine(result);
            break;
        case "SuggestDestinations":
            chatHistory.AppendLine("User:" + input);
            var recommendations = await kernel.InvokePromptAsync(input!);
            Console.WriteLine(recommendations);
            break;
        case "SuggestActivities":
            var chatSummary = await kernel.InvokeAsync(
                "ConversationSummaryPlugin",
                "SummarizeConversation",
                new() { { "input", chatHistory.ToString() } });

            var activities = await kernel.InvokePromptAsync(
                input,
                new() {
                {"input", input},
                {"history", chatSummary},
                {"ToolCallBehavior", ToolCallBehavior.AutoInvokeKernelFunctions}
            });

            chatHistory.AppendLine("User:" + input);
            chatHistory.AppendLine("Assistant:" + activities.ToString());

            Console.WriteLine(activities);
            break;
        case "HelpfulPhrases":
        case "Translate":
            var autoInvokeResult = await kernel.InvokePromptAsync(input!, new(settings));
            Console.WriteLine(autoInvokeResult);
            break;
        default:
            Console.WriteLine("Sure, I can help with that.");
            var otherIntentResult = await kernel.InvokePromptAsync(input!, new(settings));
            Console.WriteLine(otherIntentResult);
            break;
    }
}
while (!string.IsNullOrWhiteSpace(input));