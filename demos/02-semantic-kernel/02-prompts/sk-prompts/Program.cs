using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.PromptTemplates.Handlebars;

var builder = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

var configuration = builder.Build();
var model = configuration["DeploymentModel"] ?? throw new InvalidOperationException("DeploymentModel not found in configuration");
var endpoint = configuration["Endpoint"] ?? throw new InvalidOperationException("Endpoint not found in configuration");
var resourceKey = configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey not found in configuration");

Console.ForegroundColor = ConsoleColor.Green;

var userInput = "Please let me know information about Vienna";

//Create a kernel builder and add the Azure OpenAI Chat Completion service
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(model, endpoint, resourceKey)
    .Build();

// Create an inline Handlebars prompt template
Console.WriteLine("Create an inline Handlebars prompt template");
var handleBarsTemplate = HandlebarPromptBuilder.CreateHandleBarsTemplate();

var promptTemplate = await handleBarsTemplate.RenderAsync(kernel, new KernelArguments()
{
    { "input", userInput }
});

//Kernel execution
var promptResponse = await kernel.InvokePromptAsync(promptTemplate);

Console.WriteLine(promptResponse.GetValue<string>());

Console.WriteLine("Create a yaml Handlebars prompt template");
string handlebarsPromptYaml = File.ReadAllText(Path.Combine("prompts", "handlebars.prompt.yml"));

var templateFactory = new HandlebarsPromptTemplateFactory();
var function = kernel.CreateFunctionFromPrompt(
    promptTemplate: handlebarsPromptYaml,
    functionName: "HandleCustomerInquiry",
    executionSettings: new PromptExecutionSettings(),
    templateFormat: "handlebars",
    promptTemplateFactory: templateFactory);

var arguments = new KernelArguments()
{
    { "customer", new
        {
            firstName = "John",
            lastName = "Doe",
            age = 30,
            membership = "Gold",
        }
    },
    { "history", new[]
        {
            new { role = "user", content = "What is my current membership level?" },
        }
    },
};

var response = await kernel.InvokeAsync(function, arguments);
Console.WriteLine(response);

Console.ForegroundColor = ConsoleColor.Red;