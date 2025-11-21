using Azure;
using Azure.AI.OpenAI;
using AgentFwBasics.Models;
using OpenAI.Chat;

namespace AgentFwBasics.Agents;

public class AgentRunnerOpenAIChat(AppConfig config)
{
    public async Task RunAsync()
    {
        Console.WriteLine("\n" + new string('=', 70));
        Console.WriteLine("DEMO: Direct Azure OpenAI Chat (Not Agent Service)");
        Console.WriteLine(new string('=', 70));

        if (string.IsNullOrWhiteSpace(config.AzureOpenAIEndpoint) || string.IsNullOrWhiteSpace(config.AzureOpenAIApiKey))
        {
            Console.WriteLine("\n❌ Azure OpenAI configuration is missing.");
            Console.WriteLine("Please set AzureOpenAIEndpoint and AzureOpenAIApiKey in appsettings.json");
            return;
        }

        var client = new AzureOpenAIClient(
            new Uri(config.AzureOpenAIEndpoint),
            new AzureKeyCredential(config.AzureOpenAIApiKey)
        );

        var chatClient = client.GetChatClient(config.AzureOpenAIChatDeploymentName);
        var messages = new List<ChatMessage>
        {
            new SystemChatMessage("You are a helpful assistant. Be concise and clear.")
        };

        Console.WriteLine("\nAgent created (temporary, not saved to cloud)");
        Console.WriteLine("\n" + new string('=', 70));
        Console.WriteLine("Interactive Chat (Type 'quit' to exit)");
        Console.WriteLine(new string('=', 70) + "\n");

        while (true)
        {
            Console.Write("You: ");
            var userInput = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(userInput))
                continue;

            if (userInput.Trim().ToLower() is "quit" or "exit" or "q")
            {
                Console.WriteLine("\nGoodbye!");
                break;
            }

            messages.Add(new UserChatMessage(userInput));

            Console.Write("Agent: ");

            var completionOptions = new ChatCompletionOptions();
            var streamingCompletion = chatClient.CompleteChatStreamingAsync(messages, completionOptions);

            await foreach (var update in streamingCompletion)
            {
                foreach (var contentPart in update.ContentUpdate)
                {
                    Console.Write(contentPart.Text);
                }
            }

            Console.WriteLine("\n");
        }
    }
}
