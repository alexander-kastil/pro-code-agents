using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var model = configuration["DeploymentModel"];
var endpoint = configuration["Endpoint"];
var key = configuration["ApiKey"];

IKernelBuilder kernelBuilder = Kernel.CreateBuilder();

kernelBuilder.AddAzureOpenAIChatCompletion(
    deploymentName: model,
    apiKey: key,
    endpoint: endpoint
);
Kernel kernel = kernelBuilder.Build();

var chatCompletionService = kernel.GetRequiredService<IChatCompletionService>();

ChatHistory history = new ChatHistory();
history.AddSystemMessage("You are a helpful poetic assistant.");
history.AddUserMessage("Tell me a short poem about whippets and the sea.");

var response = chatCompletionService.GetStreamingChatMessageContentsAsync(
    history,
    kernel: kernel
);

await foreach (var chunk in response)
{
    Console.Write(chunk);
}

Console.WriteLine("\nNow let's try an image to demonstrate multimodal capabilities.");
byte[] bytes = File.ReadAllBytes("data/soi-beach.jpg");

history.AddUserMessage([
    new TextContent("What is this image about?"),
    new ImageContent(bytes, "image.jpg")
]);

var reply = await chatCompletionService.GetChatMessageContentAsync(history);
Console.WriteLine(reply.Content);
