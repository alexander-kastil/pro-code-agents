using System.ComponentModel.DataAnnotations;

namespace PurchasingService.Models;

public class OfferRequestDetail
{
    [Required]
    public string Product { get; set; } = string.Empty;

    [Range(1, int.MaxValue)]
    public int RequestedQuantity { get; set; }
}
