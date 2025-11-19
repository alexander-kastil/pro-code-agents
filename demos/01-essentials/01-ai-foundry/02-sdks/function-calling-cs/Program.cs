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
    new(ChatRole.System, "You are a weather chatbot. Always use Celsius. When the user asks about current, future, or past weather for any location, you MUST call the 'lookup_weather' tool with the city name (and optional zip). Do not answer weather questions without calling the tool. After receiving the tool result, summarize it plainly in Celsius."),
    new(ChatRole.User, "What is the weather in Vienna?")
};

ChatResponse response = await client.GetResponseAsync(chatHistory, chatOptions);

foreach (ChatMessage message in response.Messages)
{
    if (message.Role == ChatRole.Assistant && !string.IsNullOrWhiteSpace(message.Text))
    {
        Console.WriteLine($"Assistant >> {message.Text}");
    }
}

static WeatherReport LookupWeather(string? cityName, string? zipCode)
{
    // Favor reasonable temperature ranges per season so responses feel more natural.
    var (minTemp, maxTemp) = DateTime.UtcNow.Month switch
    {
        12 or 1 or 2 => (3, 10),
        3 or 4 or 5 => (8, 18),
        6 or 7 or 8 => (18, 30),
        _ => (10, 20)
    };

    int temperature = Random.Shared.Next(minTemp, maxTemp + 1);

    string weather = temperature switch
    {
        >= 24 => "sunny",
        >= 17 => "cloudy",
        >= 10 => "raining",
        _ => "snowing"
    };

    return new(cityName, zipCode, weather, temperature);
}

public sealed record WeatherReport(string? CityName, string? ZipCode, string Weather, int TemperatureCelsius);