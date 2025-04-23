using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

IConfiguration configuration = builder.Build();

var model = configuration["Model"];
var endpoint = configuration["Endpoint"];
var key = configuration["ApiKey"];

var kernelBuilder = Kernel.CreateBuilder();

kernelBuilder.Services.AddAzureOpenAIChatCompletion(
   model,
   endpoint,
   key
);

var kernel = kernelBuilder.Build();

while (true)
{
    Console.ForegroundColor = ConsoleColor.White;
    Console.WriteLine("\nEnter a prompt (or 'exit' to quit):");
    var prompt = Console.ReadLine();

    if (string.IsNullOrEmpty(prompt) ||
        string.Equals(prompt, "exit", StringComparison.OrdinalIgnoreCase))
    {
        break;
    }

    var result = await kernel.InvokePromptAsync(prompt);

    Console.ForegroundColor = ConsoleColor.Yellow;
    Console.WriteLine(result);
}