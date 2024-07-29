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

// Note: ChatHistory isn't working correctly as of SemanticKernel v 1.4.0
StringBuilder chatHistory = new();

kernel.ImportPluginFromType<ConversationSummaryPlugin>();
var prompts = kernel.ImportPluginFromPromptDirectory("Prompts");

