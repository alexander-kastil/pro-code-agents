namespace PurchasingService.Models;

public class OfferResponseDetail
{
    public string ProductName { get; set; } = string.Empty;

    public decimal BasePrice { get; set; }

    public decimal OfferedPrice { get; set; }

    public int RequestedQuantity { get; set; }

    public int OfferedQuantity { get; set; }

    public int DeliveryDurationDays { get; set; }

    public bool IsAvailable { get; set; }
}
