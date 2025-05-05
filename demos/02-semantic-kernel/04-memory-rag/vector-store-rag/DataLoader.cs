using System.Net;
using Microsoft.Extensions.VectorData;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Embeddings;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;
using iText.Kernel.Pdf.Canvas.Parser.Listener;
using iText.Kernel.Pdf.Xobject;

namespace VectorStoreRAG;

internal sealed class DataLoader<TKey>(
    UniqueKeyGenerator<TKey> uniqueKeyGenerator,
    IVectorStoreRecordCollection<TKey, TextSnippet<TKey>> vectorStoreRecordCollection,
    ITextEmbeddingGenerationService textEmbeddingGenerationService,
    IChatCompletionService chatCompletionService) : IDataLoader where TKey : notnull
{
    /// <inheritdoc/>
    public async Task LoadPdf(string pdfPath, int batchSize, int betweenBatchDelayInMs, CancellationToken cancellationToken)
    {
        // Create the collection if it doesn't exist.
        await vectorStoreRecordCollection.CreateCollectionIfNotExistsAsync(cancellationToken).ConfigureAwait(false);

        // Load the text and images from the PDF file and split them into batches.
        var sections = LoadTextAndImages(pdfPath, cancellationToken);
        var batches = sections.Chunk(batchSize);

        // Process each batch of content items.
        foreach (var batch in batches)
        {
            // Convert any images to text.
            var textContentTasks = batch.Select(async content =>
            {
                if (content.Text != null)
                {
                    return content;
                }

                var textFromImage = await ConvertImageToTextWithRetryAsync(
                    chatCompletionService,
                    content.Image!.Value,
                    cancellationToken).ConfigureAwait(false);
                return new RawContent { Text = textFromImage, PageNumber = content.PageNumber };
            });
            var textContent = await Task.WhenAll(textContentTasks).ConfigureAwait(false);

            // Filter out items with null or empty text BEFORE generating embeddings/records
            var validTextContent = textContent.Where(c => !string.IsNullOrWhiteSpace(c.Text)).ToList();

            // Map each paragraph to a TextSnippet and generate an embedding for it.
            // Use validTextContent instead of textContent
            var recordTasks = validTextContent.Select(async content => new TextSnippet<TKey>
            {
                Key = uniqueKeyGenerator.GenerateKey(),
                Text = content.Text,
                ReferenceDescription = $"{new FileInfo(pdfPath).Name}#page={content.PageNumber}",
                ReferenceLink = $"{new Uri(new FileInfo(pdfPath).FullName).AbsoluteUri}#page={content.PageNumber}",
                TextEmbedding = await GenerateEmbeddingsWithRetryAsync(textEmbeddingGenerationService, content.Text!, cancellationToken: cancellationToken).ConfigureAwait(false)
            });

            // Upsert the records into the vector store.
            var records = await Task.WhenAll(recordTasks).ConfigureAwait(false);

            // Since batch operations aren't available in the current version, insert records one by one
            foreach (var record in records)
            {
                var key = await vectorStoreRecordCollection.UpsertAsync(record, cancellationToken: cancellationToken).ConfigureAwait(false);
                Console.WriteLine($"Upserted record '{key}' into VectorDB");
            }

            await Task.Delay(betweenBatchDelayInMs, cancellationToken).ConfigureAwait(false);
        }
    }

    private static IEnumerable<RawContent> LoadTextAndImages(string pdfPath, CancellationToken cancellationToken)
    {
        using var pdfReader = new PdfReader(pdfPath);
        using var pdfDoc = new PdfDocument(pdfReader);
        for (int pageNum = 1; pageNum <= pdfDoc.GetNumberOfPages(); pageNum++)
        {
            if (cancellationToken.IsCancellationRequested)
            {
                break;
            }
            var page = pdfDoc.GetPage(pageNum);
            // Extract text
            var strategy = new SimpleTextExtractionStrategy();
            var text = PdfTextExtractor.GetTextFromPage(page, strategy);
            // Trim text and check IsNullOrWhiteSpace
            var trimmedText = text?.Trim();
            if (!string.IsNullOrWhiteSpace(trimmedText))
            {
                yield return new RawContent { Text = trimmedText, PageNumber = pageNum };
            }
            // Extract images
            var resources = page.GetResources();
            var xObjectDict = resources.GetResource(PdfName.XObject) as PdfDictionary;
            if (xObjectDict != null)
            {
                foreach (var xObjectName in xObjectDict.KeySet())
                {
                    var xObject = xObjectDict.GetAsStream(xObjectName);
                    if (xObject != null)
                    {
                        var subtype = xObject.GetAsName(PdfName.Subtype);
                        if (subtype != null && subtype.Equals(PdfName.Image))
                        {
                            var imgObj = new PdfImageXObject(xObject);
                            var imgBytes = imgObj.GetImageBytes(true);
                            yield return new RawContent { Image = imgBytes, PageNumber = pageNum };
                        }
                    }
                }
            }
        }
    }

    private static async Task<ReadOnlyMemory<float>> GenerateEmbeddingsWithRetryAsync(ITextEmbeddingGenerationService textEmbeddingGenerationService, string text, CancellationToken cancellationToken)
    {
        var tries = 0;

        while (true)
        {
            try
            {
                return await textEmbeddingGenerationService.GenerateEmbeddingAsync(text, cancellationToken: cancellationToken).ConfigureAwait(false);
            }
            catch (HttpOperationException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
            {
                tries++;

                if (tries < 3)
                {
                    Console.WriteLine($"Failed to generate embedding. Error: {ex}");
                    Console.WriteLine("Retrying embedding generation...");
                    await Task.Delay(10_000, cancellationToken).ConfigureAwait(false);
                }
                else
                {
                    throw;
                }
            }
        }
    }

    private static async Task<string> ConvertImageToTextWithRetryAsync(
        IChatCompletionService chatCompletionService,
        ReadOnlyMemory<byte> imageBytes,
        CancellationToken cancellationToken)
    {
        var tries = 0;

        while (true)
        {
            try
            {
                var chatHistory = new ChatHistory();
                chatHistory.AddUserMessage([
                    new TextContent("What’s in this image?"),
                    new ImageContent(imageBytes, "image/png"),
                ]);
                var result = await chatCompletionService.GetChatMessageContentsAsync(chatHistory, cancellationToken: cancellationToken).ConfigureAwait(false);
                return string.Join("\n", result.Select(x => x.Content));
            }
            catch (HttpOperationException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
            {
                tries++;

                if (tries < 3)
                {
                    Console.WriteLine($"Failed to generate text from image. Error: {ex}");
                    Console.WriteLine("Retrying text to image conversion...");
                    await Task.Delay(10_000, cancellationToken).ConfigureAwait(false);
                }
                else
                {
                    throw;
                }
            }
        }
    }

    private sealed class RawContent
    {
        public string? Text { get; init; }

        public ReadOnlyMemory<byte>? Image { get; init; }

        public int PageNumber { get; init; }
    }
}
