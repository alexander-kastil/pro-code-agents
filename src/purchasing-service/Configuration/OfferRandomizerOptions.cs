using System.Collections.Generic;

namespace PurchasingService.Services;

public sealed class OfferRandomizerOptions
{
    public decimal TransportationCost { get; set; } = 30m;

    public PricingOptions Pricing { get; set; } = new();

    public QuantityOptions Quantity { get; set; } = new();

    public DeliveryOptions Delivery { get; set; } = new();

    public Dictionary<string, decimal> BasePrices { get; set; } = new(StringComparer.OrdinalIgnoreCase);

    public sealed class PricingOptions
    {
        public double BaseProbability { get; set; } = 0.5d;
        public double DiscountProbability { get; set; } = 0.2d;
        public double MarkupProbability { get; set; } = 0.3d;
        public double DiscountMin { get; set; } = 0.01d;
        public double DiscountMax { get; set; } = 0.10d;
        public double MarkupMin { get; set; } = 0.05d;
        public double MarkupMax { get; set; } = 0.25d;
    }

    public sealed class QuantityOptions
    {
        public double FulfillProbability { get; set; } = 0.8d;
        public double ReducedProbability { get; set; } = 0.1d;
        public double UnavailableProbability { get; set; } = 0.1d;
        public double ReducedMin { get; set; } = 0.01d;
        public double ReducedMax { get; set; } = 0.30d;
    }

    public sealed class DeliveryOptions
    {
        public double CommonProbability { get; set; } = 0.7d;
        public int[] CommonDays { get; set; } = new[] { 2, 3 };
        public int AdditionalDaysBase { get; set; } = 4;
        public int AdditionalDaysRange { get; set; } = 4; // 0..(range-1) added
        public double SameDaySingleDeliveryPercentage { get; set; } = 80d;
    }
}
