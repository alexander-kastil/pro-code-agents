using Azure;
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Options;
using PurchasingService.Configuration;
using PurchasingService.Graph;
using PurchasingService.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
// Prefer a cryptographically-strong provider for less-predictable random values.
builder.Services.AddSingleton<IRandomProvider, SecureRandomProvider>();
// Bind OfferRandomizerOptions from configuration
builder.Services.Configure<OfferRandomizerOptions>(builder.Configuration.GetSection("OfferRandomizer"));
builder.Services.Configure<GraphOptions>(builder.Configuration.GetSection("Graph"));
builder.Services.Configure<AzureOpenAIOptions>(builder.Configuration.GetSection("AzureOpenAI"));
builder.Services.AddSingleton<GraphHelper>();
builder.Services.AddSingleton<IChatClient>(sp =>
{
    var aiOptions = sp.GetRequiredService<IOptions<AzureOpenAIOptions>>().Value;

    var client = new AzureOpenAIClient(
        new Uri(aiOptions.Endpoint),
        new AzureKeyCredential(aiOptions.ApiKey));

    return client.AsChatClient(aiOptions.Model);
});

// Register the IOfferRandomizer as a singleton that resolves the configured options
builder.Services.AddSingleton<IOfferRandomizer>(sp =>
{
    var options = sp.GetRequiredService<IOptions<OfferRandomizerOptions>>().Value;
    var random = sp.GetRequiredService<IRandomProvider>();
    return new OfferRandomizer(random, options);
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/swagger/v1/swagger.json", "Purchasing Service v1");
    options.RoutePrefix = string.Empty;
});

app.MapControllers();

app.Run();
