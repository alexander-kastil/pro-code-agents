using Microsoft.Extensions.Configuration;
using SalesAgentApp;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

var configuration = builder.Build();
var config = configuration.Get<AppConfig>() ?? throw new InvalidOperationException("Failed to bind configuration to AppConfig");

// var agent = new SalesAgent(config, "prompts/function_calling.md");
// await agent.RunAsync();
// await agent.DisposeAsync();

// var agent = new SalesAgent(config, "prompts/file_search.txt");
// await agent.RunAsync();
// await agent.DisposeAsync();

var agent = new SalesAgent(config, "prompts/code_interpreter.md");
await agent.RunAsync();
await agent.DisposeAsync();