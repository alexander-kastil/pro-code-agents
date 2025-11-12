using Microsoft.Extensions.Configuration;
using ConnectedAgents.Models;
using ConnectedAgentsOrchestration.Services;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();
var appConfig = ConnectedAgents.Models.OrchestrationAppConfig.FromConfiguration(configuration);

var runner = new OrchestrationRunner(appConfig);
await runner.RunAsync();
