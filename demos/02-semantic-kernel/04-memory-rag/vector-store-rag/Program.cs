using Azure;
using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.SemanticKernel;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel.Data;
using Microsoft.SemanticKernel.Embeddings;
using VectorStoreRAG;
using VectorStoreRAG.Options;
using Microsoft.SemanticKernel.Connectors.Redis;
using StackExchange.Redis;

// Use HostApplicationBuilder for DI and kernel setup
var builder = Host.CreateApplicationBuilder(args);
builder.Configuration.SetBasePath(Directory.GetCurrentDirectory());
builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

// Create strongly typed config using ApplicationConfig
var appConfig = new ApplicationConfig(builder.Configuration);

// Configure options
builder.Services.Configure<RagConfig>(builder.Configuration.GetSection(RagConfig.ConfigSectionName));

// Register the kernel with DI and add services
var kernelBuilder = builder.Services.AddKernel();

// Use top-level Endpoint and ApiKey, and AzureKeyCredential
kernelBuilder.AddAzureOpenAIChatCompletion(
    appConfig.AzureOpenAIConfig.DeploymentName, // Use corrected property name
    appConfig.Endpoint, // Use top-level endpoint
    appConfig.ApiKey); // Use top-level API key

// Use top-level Endpoint and ApiKey
kernelBuilder.AddAzureOpenAITextEmbeddingGeneration(
    appConfig.AzureOpenAIEmbeddingsConfig.DeploymentName,
    appConfig.Endpoint,
    appConfig.ApiKey);

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

// Register VectorStoreTextSearch directly as a singleton
// The DI container will resolve IVectorStoreRecordCollection and ITextEmbeddingGenerationService
builder.Services.AddSingleton<VectorStoreTextSearch<TextSnippet<string>>>();

// Register UniqueKeyGenerator<string> for DI
builder.Services.AddSingleton(new UniqueKeyGenerator<string>(() => Guid.NewGuid().ToString()));

// Register IDataLoader for DI
builder.Services.AddSingleton<IDataLoader, DataLoader<string>>();

// Register RAGChatService as a hosted service
builder.Services.AddSingleton<IHostedService>(sp =>
{
    // Resolve required services from the service provider
    var dataLoader = sp.GetRequiredService<IDataLoader>();
    var vectorStoreTextSearch = sp.GetRequiredService<VectorStoreTextSearch<TextSnippet<string>>>();
    var kernel = sp.GetRequiredService<Kernel>();
    var ragConfigOptions = sp.GetRequiredService<IOptions<RagConfig>>();
    var appShutdownCts = new CancellationTokenSource();
    return new RAGChatService<string>(dataLoader, vectorStoreTextSearch, kernel, ragConfigOptions, appShutdownCts);
});

// Build and run the host
using IHost host = builder.Build();
await host.RunAsync();