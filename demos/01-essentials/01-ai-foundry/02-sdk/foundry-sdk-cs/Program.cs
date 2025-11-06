using Azure;
using Azure.Identity;
using Azure.Core;
using Azure.Core.Pipeline;
using Azure.AI.OpenAI;
using Azure.AI.Projects;
using Azure.AI.Inference;
using OpenAI.Chat;
using System.ClientModel.Primitives;
using OpenAI;
using Microsoft.Extensions.Configuration;

#pragma warning disable OPENAI001 //currently required for token based authentication

IConfiguration configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .Build();

var model = configuration["Model"];
var endpoint = configuration["AzureOpenAIEndpoint"];

BearerTokenPolicy tokenPolicy = new(
    new DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default");

ChatClient client = new(
    model: model,
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions()
    {

        Endpoint = new Uri(endpoint + "/openai/v1")
    }
);

ChatCompletionOptions options = new ChatCompletionOptions
{
    ReasoningEffortLevel = ChatReasoningEffortLevel.Low,
    MaxOutputTokenCount = 100000
};

ChatCompletion completion = client.CompleteChat(
         new DeveloperChatMessage("You are a helpful assistant that knows about gym, workouts, and fitness."),
         new UserChatMessage("What kinds of protein do you know about? Just a short list please.")
    );

Console.WriteLine($"[ASSISTANT]: {completion.Content[0].Text}");