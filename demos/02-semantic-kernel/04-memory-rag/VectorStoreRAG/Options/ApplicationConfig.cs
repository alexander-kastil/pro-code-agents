// Copyright (c) Microsoft. All rights reserved.

using Microsoft.Extensions.Configuration;

namespace VectorStoreRAG.Options;

/// <summary>
/// Helper class to load all configuration settings for the VectorStoreRAG project.
/// </summary>
internal sealed class ApplicationConfig
{
    // Rename section constant
    private const string AzureAIServicesSectionName = "AzureAIServices";

    // Add properties for top-level ApiKey and Endpoint
    private string _apiKey = string.Empty;
    private string _endpoint = string.Empty;

    private readonly AzureOpenAIConfig _azureOpenAIConfig = new();
    private readonly AzureOpenAIEmbeddingsConfig _azureOpenAIEmbeddingsConfig = new();
    private readonly RagConfig _ragConfig = new();
    private readonly AzureAISearchConfig _azureAISearchConfig = new();
    private readonly AzureCosmosDBConfig _azureCosmosDBNoSQLConfig = new();
    private readonly RedisConfig _redisConfig = new();

    public ApplicationConfig(ConfigurationManager configurationManager)
    {
        // Bind top-level properties
        var azureAIServicesSection = configurationManager.GetRequiredSection(AzureAIServicesSectionName);
        this._apiKey = azureAIServicesSection.GetValue<string>("ApiKey") ?? string.Empty;
        this._endpoint = azureAIServicesSection.GetValue<string>("Endpoint") ?? string.Empty;

        // Bind subsections
        azureAIServicesSection
            .GetRequiredSection(AzureOpenAIConfig.ConfigSectionName)
            .Bind(this._azureOpenAIConfig);
        azureAIServicesSection
            .GetRequiredSection(AzureOpenAIEmbeddingsConfig.ConfigSectionName)
            .Bind(this._azureOpenAIEmbeddingsConfig);

        // Keep existing bindings for other sections
        configurationManager
            .GetRequiredSection(RagConfig.ConfigSectionName)
            .Bind(this._ragConfig);
        configurationManager
            .GetRequiredSection($"VectorStores:{AzureAISearchConfig.ConfigSectionName}")
            .Bind(this._azureAISearchConfig);
        configurationManager
            .GetRequiredSection($"VectorStores:{AzureCosmosDBConfig.NoSQLConfigSectionName}")
            .Bind(this._azureCosmosDBNoSQLConfig);
        configurationManager
            .GetRequiredSection($"VectorStores:{RedisConfig.ConfigSectionName}")
            .Bind(this._redisConfig);
    }

    // Add public accessors for ApiKey and Endpoint
    public string ApiKey => this._apiKey;
    public string Endpoint => this._endpoint;

    public AzureOpenAIConfig AzureOpenAIConfig => this._azureOpenAIConfig;
    public AzureOpenAIEmbeddingsConfig AzureOpenAIEmbeddingsConfig => this._azureOpenAIEmbeddingsConfig;
    public RagConfig RagConfig => this._ragConfig;
    public AzureAISearchConfig AzureAISearchConfig => this._azureAISearchConfig;
    public AzureCosmosDBConfig AzureCosmosDBNoSQLConfig => this._azureCosmosDBNoSQLConfig;
    public RedisConfig RedisConfig => this._redisConfig;
}
