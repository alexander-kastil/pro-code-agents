using System.ComponentModel.DataAnnotations;

namespace PurchasingService.Models;

public class OfferRequest
{
    [Required]
    public int SupplierId { get; set; }

    [Required]
    public List<OfferRequestDetail> RequestDetails { get; set; } = new();

    [EmailAddress]
    public string? Email { get; set; }
}
