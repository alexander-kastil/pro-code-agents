using Azure;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.SemanticKernel;
using VectorStoreRAG;
using VectorStoreRAG.Options;

// Use HostApplicationBuilder for DI and kernel setup
var builder = Host.CreateApplicationBuilder(args);
builder.Configuration.SetBasePath(Directory.GetCurrentDirectory());
builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

// Bind config
var appConfig = builder.Configuration.Get<ApplicationConfig>();

// Register the kernel with DI and add services
var kernelBuilder = builder.Services.AddKernel();

kernelBuilder.AddAzureOpenAIChatCompletion(
    appConfig.AzureOpenAIConfig.ChatDeploymentName,
    appConfig.AzureOpenAIConfig.Endpoint,
    new AzureCliCredential());

kernelBuilder.AddAzureOpenAITextEmbeddingGeneration(
    appConfig.AzureOpenAIEmbeddingsConfig.DeploymentName,
    appConfig.AzureOpenAIEmbeddingsConfig.Endpoint,
    new AzureCliCredential());

switch (appConfig.RagConfig.VectorStoreType)
{
    case "AzureAISearch":
        kernelBuilder.AddAzureAISearchVectorStoreRecordCollection<TextSnippet<string>>(
            appConfig.RagConfig.CollectionName,
            new Uri(appConfig.AzureAISearchConfig.Endpoint),
            new AzureKeyCredential(appConfig.AzureAISearchConfig.ApiKey));
        break;
    case "AzureCosmosDBNoSQL":
        kernelBuilder.AddAzureCosmosDBNoSQLVectorStoreRecordCollection<TextSnippet<string>>(
            appConfig.RagConfig.CollectionName,
            appConfig.AzureCosmosDBNoSQLConfig.ConnectionString,
            appConfig.AzureCosmosDBNoSQLConfig.DatabaseName);
        break;
    case "InMemory":
        kernelBuilder.AddInMemoryVectorStoreRecordCollection<string, TextSnippet<string>>(
            appConfig.RagConfig.CollectionName);
        break;
    case "Redis":
        kernelBuilder.AddRedisJsonVectorStoreRecordCollection<TextSnippet<string>>(
            appConfig.RagConfig.CollectionName,
            appConfig.RedisConfig.ConnectionConfiguration);
        break;
    default:
        throw new NotSupportedException($"Vector store type '{appConfig.RagConfig.VectorStoreType}' is not supported.");
}

// Build and run the host
using IHost host = builder.Build();
await host.RunAsync();
