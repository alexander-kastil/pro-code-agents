namespace PurchasingService.Configuration;

public class AzureOpenAIOptions
{
    public string Model { get; set; } = string.Empty;

    public string Endpoint { get; set; } = string.Empty;

    public string ApiKey { get; set; } = string.Empty;
}
