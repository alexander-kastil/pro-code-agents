namespace VectorStoreRAG;

internal interface IDataLoader
{
    Task LoadPdf(string pdfPath, int batchSize, int betweenBatchDelayInMs, CancellationToken cancellationToken);
}
