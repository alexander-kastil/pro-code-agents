using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Configuration;

IConfiguration configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json", optional: false)
    .Build();

var endpoint = configuration["AzureOpenAIEndpoint"];
var model = configuration["Model"];

if (string.IsNullOrWhiteSpace(endpoint) || string.IsNullOrWhiteSpace(model))
{
    Console.WriteLine("Configure AzureOpenAIEndpoint and Model in appsettings.json before running the sample.");
    return;
}

var azureOpenAIClient = new AzureOpenAIClient(new Uri(endpoint), new DefaultAzureCredential());

IChatClient client = new ChatClientBuilder(
        azureOpenAIClient.GetChatClient(model).AsIChatClient())
    .UseFunctionInvocation()
    .Build();

var chatOptions = new ChatOptions
{
    Tools =
    [
        // Expose the lookup_weather function to the model so it can fetch weather details.
        AIFunctionFactory.Create(
            (string? cityName, string? zipCode) => LookupWeather(cityName, zipCode),
            "lookup_weather",
            "Lookup the weather for a given city name or zip code.")
    ]
};

var chatHistory = new List<ChatMessage>
{
    new(ChatRole.System, "You are a weather chatbot. Always respond using Celsius only; never mention Fahrenheit."),
    new(ChatRole.User, "is it sunny in Berkeley CA?")
};

ChatResponse response = await client.GetResponseAsync(chatHistory, chatOptions);

foreach (ChatMessage message in response.Messages)
{
    if (message.Role == ChatRole.Assistant && !string.IsNullOrWhiteSpace(message.Text))
    {
        Console.WriteLine($"Assistant >>> {message.Text}");
    }
}

static WeatherReport LookupWeather(string? cityName, string? zipCode) => new(
    CityName: cityName,
    ZipCode: zipCode,
    Weather: "sunny",
    TemperatureCelsius: 24);

internal sealed record WeatherReport(string? CityName, string? ZipCode, string Weather, int TemperatureCelsius);