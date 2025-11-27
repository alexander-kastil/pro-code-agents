using Microsoft.Extensions.AI;
using Azure.Identity;
using OpenAI;
using System.ClientModel.Primitives;
using ChatMessage = Microsoft.Extensions.AI.ChatMessage;

#pragma warning disable OPENAI001   // currently required for token-based authentication against Azure OpenAI

/// <summary>
/// Multi-turn Interactive Chat with Azure AI Model Router
/// 
/// This demo demonstrates:
/// - Interactive console-based chat session with conversation history
/// - Using Azure AI Foundry's model router to automatically select the best model for each turn
/// - Maintaining context across multiple turns with a rolling history window
/// - Displaying which underlying model was selected by the router for each response
/// - Configurable parameters (temperature, max tokens, history size) via appsettings.json
/// 
/// The model router intelligently selects from available models based on the request characteristics,
/// and the response Model property reveals which specific model handled each turn.
/// </summary>
public class ChatModelRouterMultiturn
{
    public async Task Run(
        string modelRouter, 
        string endpoint,
        string systemPrompt = "You are a helpful assistant.",
        int maxHistoryTurns = 12,
        int maxOutputTokens = 10000,
        float temperature = 0.7f,
        float topP = 0.95f,
        float frequencyPenalty = 0.0f,
        float presencePenalty = 0.0f)
    {
        // Create a BearerTokenPolicy using DefaultAzureCredential (Azure AD)
        var tokenPolicy = new BearerTokenPolicy(
            new DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default");

        // Create the OpenAI ChatClient pointing at Azure OpenAI's OpenAI-compatible endpoint
        var chatClient = new OpenAI.Chat.ChatClient(
            model: modelRouter,
            authenticationPolicy: tokenPolicy,
            options: new OpenAIClientOptions
            {
                // Azure OpenAI compatible path
                Endpoint = new Uri(endpoint.TrimEnd('/') + "/openai/v1")
            }
        );

        // Adapt the OpenAI ChatClient to Microsoft.Extensions.AI's IChatClient
        IChatClient client = chatClient.AsIChatClient();

        // Conversation state: always begin with system message
        var messages = new List<ChatMessage>
        {
            new ChatMessage(ChatRole.System, systemPrompt)
        };

        Console.WriteLine("Interactive chat started. Type 'exit' or 'quit' to stop.\n");

        while (true)
        {
            Console.Write("You: ");
            var userInput = Console.ReadLine()?.Trim();

            if (string.IsNullOrEmpty(userInput))
            {
                continue;
            }

            if (userInput.Equals("exit", StringComparison.OrdinalIgnoreCase) ||
                userInput.Equals("quit", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("Goodbye.");
                break;
            }

            // Append user turn
            messages.Add(new ChatMessage(ChatRole.User, userInput));

            // Trim history to keep context small while preserving the system message
            var trimmedMessages = TrimHistory(messages, maxHistoryTurns);

            // Prepare chat options
            var options = new ChatOptions
            {
                MaxOutputTokens = maxOutputTokens,
                Temperature = temperature,
                TopP = topP,
                FrequencyPenalty = frequencyPenalty,
                PresencePenalty = presencePenalty
            };

            // Call the router deployment
            ChatResponse response = await client.GetResponseAsync(trimmedMessages, options);

            var assistantMessage = response.Messages.FirstOrDefault(m => m.Role == ChatRole.Assistant)?.Text ?? "";
            var routedModel = response.ModelId ?? "<unknown>";

            Console.WriteLine("=" + new string('=', 49));
            Console.WriteLine($"Model chosen by the router: {routedModel}");
            Console.WriteLine("=" + new string('=', 49));
            Console.WriteLine($"Assistant: {assistantMessage}\n");

            // Append assistant turn to the full history
            messages.Add(new ChatMessage(ChatRole.Assistant, assistantMessage));
        }
    }

    /// <summary>
    /// Keep system message plus the last N user/assistant turns.
    /// </summary>
    /// <param name="messages">Full history including system at index 0</param>
    /// <param name="maxHistoryTurns">Number of recent user+assistant pairs to retain</param>
    /// <returns>Trimmed list of messages</returns>
    private List<ChatMessage> TrimHistory(List<ChatMessage> messages, int maxHistoryTurns)
    {
        if (messages.Count == 0)
        {
            return messages;
        }

        // Always preserve the first message if it is the system message
        var head = messages.Take(1).ToList();
        var body = messages.Skip(1).ToList();

        // Count pairs in body. We'll keep the last 2*maxHistoryTurns messages
        int keep = maxHistoryTurns * 2;
        
        if (body.Count <= keep)
        {
            return head.Concat(body).ToList();
        }
        else
        {
            return head.Concat(body.Skip(body.Count - keep)).ToList();
        }
    }
}
