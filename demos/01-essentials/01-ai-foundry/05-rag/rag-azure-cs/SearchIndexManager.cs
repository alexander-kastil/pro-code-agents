using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace RagAzure;

public class SearchIndexManager
{
    private readonly SearchIndexClient _searchIndexClient;
    private readonly string _indexName;

    public SearchIndexManager(SearchIndexClient searchIndexClient, string indexName)
    {
        _searchIndexClient = searchIndexClient;
        _indexName = indexName;
    }

    public async Task<bool> CreateSearchIndexAsync(string embeddingsModel)
    {
        Console.WriteLine("\n## 3. Create Azure AI Search Index with Integrated Vectorization");
        Console.WriteLine($"🚀 Creating search index with manual embeddings using Azure AI Project");
        Console.WriteLine($"🤖 Embeddings model: {embeddingsModel}");
        
        var vectorSearch = new VectorSearch();
        vectorSearch.Algorithms.Add(new HnswAlgorithmConfiguration("insurance-algorithm"));
        vectorSearch.Algorithms.Add(new ExhaustiveKnnAlgorithmConfiguration("insurance-eknn"));
        vectorSearch.Profiles.Add(new VectorSearchProfile("insurance-profile", "insurance-algorithm"));
        
        var semanticConfig = new SemanticConfiguration(
            "insurance-semantic",
            new SemanticPrioritizedFields
            {
                TitleField = new SemanticField("title"),
                ContentFields =
                {
                    new SemanticField("content")
                },
                KeywordsFields =
                {
                    new SemanticField("category"),
                    new SemanticField("file_name")
                }
            });
        
        var semanticSearch = new SemanticSearch();
        semanticSearch.Configurations.Add(semanticConfig);
        
        var fields = new List<SearchField>
        {
            new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
            new SearchableField("title") { IsFilterable = false, IsSortable = false },
            new SearchableField("content") { IsFilterable = false, IsSortable = false },
            new SearchableField("category") { IsFilterable = true, IsFacetable = true },
            new SearchableField("file_name") { IsFilterable = true },
            new SimpleField("file_type", SearchFieldDataType.String) { IsFilterable = true },
            new SimpleField("chunk_id", SearchFieldDataType.Int32),
            new SimpleField("chunk_count", SearchFieldDataType.Int32),
            new SimpleField("original_length", SearchFieldDataType.Int32),
            new SimpleField("chunk_length", SearchFieldDataType.Int32),
            new SimpleField("processing_date", SearchFieldDataType.DateTimeOffset),
            new SearchField("content_vector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
            {
                IsSearchable = true,
                VectorSearchDimensions = 1536,
                VectorSearchProfileName = "insurance-profile"
            }
        };
        
        var index = new SearchIndex(_indexName)
        {
            Fields = fields,
            VectorSearch = vectorSearch,
            SemanticSearch = semanticSearch
        };
        
        var result = await _searchIndexClient.CreateOrUpdateIndexAsync(index);
        
        Console.WriteLine($"✅ Search index '{_indexName}' created successfully!");
        Console.WriteLine($"📋 Index fields: {result.Value.Fields.Count}");
        Console.WriteLine($"🔍 Vector search enabled: {result.Value.VectorSearch != null}");
        Console.WriteLine($"🧠 Semantic search enabled: {result.Value.SemanticSearch != null}");
        Console.WriteLine($"📝 Embeddings will be generated manually using Azure AI Project");
        
        return true;
    }

    public async Task<bool> DeleteIndexIfExistsAsync()
    {
        try
        {
            await _searchIndexClient.DeleteIndexAsync(_indexName);
            Console.WriteLine($"✅ Deleted existing index: {_indexName}");
            return true;
        }
        catch (RequestFailedException ex) when (ex.Status == 404)
        {
            Console.WriteLine($"ℹ️ Index {_indexName} doesn't exist - will create new");
            return true;
        }
    }

    public async Task<Dictionary<string, object>> GetIndexStatsAsync()
    {
        try
        {
            var index = await _searchIndexClient.GetIndexAsync(_indexName);
            var stats = await _searchIndexClient.GetIndexStatisticsAsync(_indexName);
            
            return new Dictionary<string, object>
            {
                ["name"] = index.Value.Name,
                ["field_count"] = index.Value.Fields.Count,
                ["document_count"] = stats.Value.DocumentCount,
                ["storage_size"] = stats.Value.StorageSize
            };
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error getting index stats: {ex.Message}");
            return new Dictionary<string, object>();
        }
    }
}
