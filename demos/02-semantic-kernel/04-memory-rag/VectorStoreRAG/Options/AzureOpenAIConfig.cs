// Copyright (c) Microsoft. All rights reserved.

using System.ComponentModel.DataAnnotations;

namespace VectorStoreRAG.Options;

/// <summary>
/// Azure OpenAI service settings.
/// </summary>
internal sealed class AzureOpenAIConfig
{
    public const string ConfigSectionName = "AzureOpenAI";

    [Required]
    public string DeploymentName { get; set; } = string.Empty;
}
