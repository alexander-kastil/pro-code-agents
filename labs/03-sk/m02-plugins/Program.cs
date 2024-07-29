using System;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Plugins.Core;

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

skBuilder.Plugins.AddFromType<ConversationSummaryPlugin>();

var prompts = kernel.ImportPluginFromPromptDirectory("Prompts/TravelPlugins");

ChatHistory history = [];
string input = @"I'm planning an anniversary trip with my spouse. We like hiking, 
    mountains, and beaches. Our travel budget is $15000";

var result = await kernel.InvokeAsync<string>(prompts["SuggestedDestinations"],
    new() { { "history", history }, { "destination", input } });

Console.WriteLine(result);

history.AddUserMessage(input);
history.AddAssistantMessage(result);
Console.WriteLine("No suggestions found");
