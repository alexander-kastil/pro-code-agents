using System.ComponentModel.DataAnnotations;

namespace PurchasingService.Models;

public class OrderDetail
{
    [Required]
    public string ProductName { get; set; } = string.Empty;

    [Range(0.01, double.MaxValue)]
    public decimal Price { get; set; }

    [Range(1, int.MaxValue)]
    public int Quantity { get; set; }
}
