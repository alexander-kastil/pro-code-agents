// Copyright (c) Microsoft. All rights reserved.

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Data;
using Microsoft.SemanticKernel.PromptTemplates.Handlebars;
using VectorStoreRAG.Options;
using System.Diagnostics;

namespace VectorStoreRAG;

internal sealed class RAGChatService<TKey>(
    IDataLoader dataLoader,
    VectorStoreTextSearch<TextSnippet<TKey>> vectorStoreTextSearch,
    Kernel kernel,
    IOptions<RagConfig> ragConfigOptions,
    [FromKeyedServices("AppShutdown")] CancellationTokenSource appShutdownCancellationTokenSource) : IHostedService
{
    private Task? _dataLoaded;
    private Task? _chatLoop;
    public Task StartAsync(CancellationToken cancellationToken)
    {
        // Start to load all the configured PDFs into the vector store.
        if (ragConfigOptions.Value.BuildCollection)
        {
            this._dataLoaded = this.LoadDataAsync(cancellationToken);
        }
        else
        {
            this._dataLoaded = Task.CompletedTask;
        }

        // Start the chat loop.
        this._chatLoop = this.ChatLoopAsync(cancellationToken);

        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        return Task.CompletedTask;
    }

    private async Task ChatLoopAsync(CancellationToken cancellationToken)
    {
        var pdfFiles = string.Join(", ", ragConfigOptions.Value.PdfFilePaths ?? []);

        // Wait for the data to be loaded before starting the chat loop.
        while (this._dataLoaded != null && !this._dataLoaded.IsCompleted && !cancellationToken.IsCancellationRequested)
        {
            await Task.Delay(1_000, cancellationToken).ConfigureAwait(false);
        }

        // If data loading failed, don't start the chat loop.
        if (this._dataLoaded != null && this._dataLoaded.IsFaulted)
        {
            Console.WriteLine("Failed to load data");
            return;
        }

        Console.WriteLine("PDF loading complete\n");

        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine("Assistant > Press enter with no prompt to exit.");

        // Add a search plugin to the kernel which we will use in the template below
        // to do a vector search for related information to the user query.
        kernel.Plugins.Add(vectorStoreTextSearch.CreateWithGetTextSearchResults("SearchPlugin"));

        // Start the chat loop.
        while (!cancellationToken.IsCancellationRequested)
        {
            // Prompt the user for a question.
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"Assistant > What would you like to know from the loaded PDFs: ({pdfFiles})?");

            // Read the user question.
            Console.ForegroundColor = ConsoleColor.White;
            Console.Write("User > ");
            var question = Console.ReadLine();

            // Exit the application if the user didn't type anything.
            if (string.IsNullOrWhiteSpace(question))
            {
                appShutdownCancellationTokenSource.Cancel();
                break;
            }

            // --- Debugging: Inspect parameters before invoking prompt ---
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("\n--- Debugging Prompt Parameters ---");
            Console.WriteLine($"Question Argument: {question}");

            // Manually invoke the search function to see its results
            Console.WriteLine("[DEBUG] Calling GetTextSearchResultsAsync..."); // Removed limit info
            var searchStopwatch = Stopwatch.StartNew();
            // Remove limit parameter from the call
            var searchResults = await vectorStoreTextSearch.GetTextSearchResultsAsync(question, cancellationToken: cancellationToken);
            searchStopwatch.Stop();
            Console.WriteLine($"[DEBUG] GetTextSearchResultsAsync completed in {searchStopwatch.ElapsedMilliseconds}ms.");

            Console.WriteLine("Search Plugin Results:");

            // Use await foreach directly on searchResults.Results
            bool resultsFound = false;
            Console.WriteLine("[DEBUG] Starting iteration over search results (await foreach)...");
            var iterationStopwatch = Stopwatch.StartNew();
            await foreach (var result in searchResults.Results)
            {
                resultsFound = true; // Set flag if we enter the loop
                Console.WriteLine($"  Name: {result.Name}");
                Console.WriteLine($"  Value: {result.Value?.Substring(0, Math.Min(result.Value.Length, 100))}..."); // Display first 100 chars
                Console.WriteLine($"  Link: {result.Link}");
                Console.WriteLine("  -----------------");
            }
            iterationStopwatch.Stop();
            Console.WriteLine($"[DEBUG] Iteration over search results completed in {iterationStopwatch.ElapsedMilliseconds}ms.");

            if (!resultsFound)
            {
                Console.WriteLine("  (No results found)");
            }
            Console.WriteLine("--- End Debugging ---\n");
            // --- End Debugging ---

            // Invoke the LLM with a template that uses the search plugin to
            Console.WriteLine("[DEBUG] Calling InvokePromptStreamingAsync...");
            var llmStopwatch = Stopwatch.StartNew();
            var response = kernel.InvokePromptStreamingAsync(
                promptTemplate: """
                    Please use this information to answer the question:
                    {{#with (SearchPlugin-GetTextSearchResults question)}}  
                      {{#each this}}  
                        Name: {{Name}}
                        Value: {{Value}}
                        Link: {{Link}}
                        -----------------
                      {{/each}}
                    {{/with}}

                    Include citations to the relevant information where it is referenced in the response.
                    
                    Question: {{question}}
                    """,
                arguments: new KernelArguments()
                {
                    { "question", question },
                },
                templateFormat: "handlebars",
                promptTemplateFactory: new HandlebarsPromptTemplateFactory(),
                cancellationToken: cancellationToken);

            // Stream the LLM response to the console with error handling.
            Console.ForegroundColor = ConsoleColor.Green;
            Console.Write("\nAssistant > ");

            try
            {
                Console.WriteLine("[DEBUG] Starting iteration over LLM response stream...");
                await foreach (var message in response.ConfigureAwait(false))
                {
                    // Log first message received time
                    if (llmStopwatch.IsRunning)
                    {
                        llmStopwatch.Stop();
                        Console.WriteLine($"\n[DEBUG] First LLM response chunk received after {llmStopwatch.ElapsedMilliseconds}ms.");
                        Console.Write("Assistant > "); // Re-print prompt start after debug info
                    }
                    Console.Write(message);
                }
                Console.WriteLine();
                // Ensure stopwatch is stopped if loop finishes or was empty
                if (llmStopwatch.IsRunning) llmStopwatch.Stop();
                Console.WriteLine("[DEBUG] Finished iterating over LLM response stream.");
            }
            catch (Exception ex)
            {
                // Ensure stopwatch is stopped in case of error
                if (llmStopwatch.IsRunning) llmStopwatch.Stop();
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"Call to LLM failed with error: {ex}");
            }
        }
    }

    private async Task LoadDataAsync(CancellationToken cancellationToken)
    {
        try
        {
            foreach (var pdfFilePath in ragConfigOptions.Value.PdfFilePaths ?? [])
            {
                Console.WriteLine($"Loading PDF into vector store: {pdfFilePath}");
                await dataLoader.LoadPdf(
                    pdfFilePath,
                    ragConfigOptions.Value.DataLoadingBatchSize,
                    ragConfigOptions.Value.DataLoadingBetweenBatchDelayInMilliseconds,
                    cancellationToken).ConfigureAwait(false);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to load PDFs: {ex}");
            throw;
        }
    }
}
