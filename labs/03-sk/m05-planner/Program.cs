using System;
using System.IO;
using Microsoft.Extensions.Configuration;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.PromptTemplates.Handlebars;
using Microsoft.SemanticKernel.Planning.Handlebars;

var builder = new ConfigurationBuilder()
    .AddJsonFile($"appsettings.json", true, true);
IConfigurationRoot configuration = builder.Build();

var model = configuration["SemanticKernel:DeploymentModel"];
var endpoint = configuration["SemanticKernel:Endpoint"];
var key = configuration["SemanticKernel:ApiKey"];

bool plan = false;

var skBuilder = Kernel.CreateBuilder();
skBuilder.AddAzureOpenAIChatCompletion(
    model,
    endpoint,
    key);
var kernel = skBuilder.Build();

kernel.ImportPluginFromType<MusicLibraryPlugin>();
kernel.ImportPluginFromType<MusicConcertPlugin>();
kernel.ImportPluginFromPromptDirectory("Prompts");

var songSuggesterFunction = kernel.CreateFunctionFromPrompt(
    promptTemplate: @"Based on the user's recently played music:
        {{$recentlyPlayedSongs}}
        recommend a song to the user from the music library:
        {{$musicLibrary}}",
    functionName: "SuggestSong",
    description: "Suggest a song to the user"
);

kernel.Plugins.AddFromFunctions("SuggestSongPlugin", [songSuggesterFunction]);

if (plan)
{
    var planner = new HandlebarsPlanner(new HandlebarsPlannerOptions() { AllowLoops = true });

    string location = "Redmond WA USA";
    string goal = @$"Based on the user's recently played music, suggest a 
        concert for the user living in ${location}";

    var concertPlan = await planner.CreatePlanAsync(kernel, goal);
    Console.WriteLine($"Plan: {concertPlan}");

    var result = await concertPlan.InvokeAsync(kernel);

    Console.WriteLine($"Results: {result}");

    var songSuggestPlan = await planner.CreatePlanAsync(kernel, @"Suggest a song from the 
        music library to the user based on their recently played songs");

    Console.WriteLine("Song Plan:");
    Console.WriteLine(songSuggestPlan);
}
else
{
    string dir = Directory.GetCurrentDirectory();
    string template = File.ReadAllText($"{dir}/handlebarsTemplate.txt");

    var handlebarsPromptFunction = kernel.CreateFunctionFromPrompt(
        new()
        {
            Template = template,
            TemplateFormat = "handlebars"
        }, new HandlebarsPromptTemplateFactory()
    );

    string location = "Redmond WA USA";
    var templateResult = await kernel.InvokeAsync(handlebarsPromptFunction,
        new() {
        { "location", location },
        { "suggestConcert", false }
        });

    Console.WriteLine(templateResult);
}