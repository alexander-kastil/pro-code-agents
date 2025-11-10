using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol.Transport;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var model = configuration["Model"] ?? throw new InvalidOperationException("Model configuration is missing");
var endpoint = configuration["Endpoint"] ?? throw new InvalidOperationException("Endpoint configuration is missing");
var key = configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey configuration is missing");
var repo = configuration["GitRepo"] ?? throw new InvalidOperationException("Repo configuration is missing");

// Create an MCPClient for the GitHub server
await using var mcpClient = await McpClientFactory.CreateAsync(new StdioClientTransport(new()
{
    Name = "MCPServer",
    Command = "npx",
    Arguments = ["-y", "@modelcontextprotocol/server-github"],
}));

// Retrieve the list of tools available on the GitHub server
var tools = await mcpClient.ListToolsAsync().ConfigureAwait(false);
foreach (var tool in tools)
{
    Console.WriteLine($"{tool.Name}: {tool.Description}");
}

// Prepare and build kernel with the MCP tools as Kernel functions
var kernelBuilder = Kernel.CreateBuilder();
kernelBuilder.Services.AddAzureOpenAIChatCompletion(
    deploymentName: model,
    endpoint: endpoint,
    apiKey: key
);
Kernel kernel = kernelBuilder.Build();
kernel.Plugins.AddFromFunctions("GitHub", tools.Select(aiFunction => aiFunction.AsKernelFunction()));

// Enable automatic function calling
OpenAIPromptExecutionSettings executionSettings = new()
{
    Temperature = 0,
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(options: new() { RetainArgumentTypes = true })
};

// Test using GitHub tools
var prompt = $"Summarize the last commit to the {repo} repository?";
var result = await kernel.InvokePromptAsync(prompt, new(executionSettings)).ConfigureAwait(false);
Console.WriteLine($"\n\n{prompt}\n{result}");

// Define the agent
ChatCompletionAgent agent = new()
{
    Instructions = "Answer questions about GitHub repositories.",
    Name = "GitHubAgent",
    Kernel = kernel,
    Arguments = new KernelArguments(executionSettings),
};

// Respond to user input, invoking functions where appropriate.
ChatMessageContent response = await agent.InvokeAsync(prompt).FirstAsync();
Console.WriteLine($"\n\nResponse from GitHubAgent:\n{response.Content}");

// Summarize the last five pull requests in the alexander-kastil/github-copilot-skills-fest repository.
prompt = $"Summarize the last pull requests in the {repo} repository?";
response = await agent.InvokeAsync(prompt).FirstAsync();
Console.WriteLine($"\n\nResponse from GitHubAgent:\n{response.Content}");


prompt = $"Summarize the last issue in the {repo} repository?";
response = await agent.InvokeAsync(prompt).FirstAsync();
Console.WriteLine($"\n\nResponse from GitHubAgent:\n{response.Content}");