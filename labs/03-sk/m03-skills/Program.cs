using System;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;

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
var result = await kernel.InvokePromptAsync(
    "Give me a list of breakfast foods with eggs and cheese");
    
Console.WriteLine(result);