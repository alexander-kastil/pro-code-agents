namespace PurchasingService.Models;

public class OfferResponse
{
    public Guid Id { get; set; } = Guid.NewGuid();

    public int SupplierId { get; set; }

    public decimal TransportationCost { get; set; }

    public DateTimeOffset Timestamp { get; set; }

    public IReadOnlyList<OfferResponseDetail> RequestDetails { get; set; } = Array.Empty<OfferResponseDetail>();

    public string? Email { get; set; }
}
