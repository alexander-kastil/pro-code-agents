using AgentWorkshop.Client;
using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

var configuration = builder.Build();
var conProject = configuration["Project_ConnectionString"] ?? throw new InvalidOperationException("Project_ConnectionString not found in configuration");
var model = configuration["Model"] ?? throw new InvalidOperationException("Model not found in configuration");

AIProjectClient projectClient = new(conProject, new DefaultAzureCredential());

var agent = new SalesAgent(projectClient, model, "prompts/function_calling.txt");
await agent.RunAsync();
