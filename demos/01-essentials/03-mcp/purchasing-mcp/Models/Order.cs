using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace PurchasingService.Models;

public class Order
{
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    public string RequestId { get; set; } = string.Empty;

    [Range(1, int.MaxValue)]
    public int SupplierId { get; set; }

    [Required]
    public DateTime Date { get; set; }

    [MinLength(1)]
    public List<OrderDetail> OrderDetails { get; set; } = new();
}
