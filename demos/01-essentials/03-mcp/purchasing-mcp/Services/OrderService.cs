using PurchasingService.Data;
using PurchasingService.Models;

namespace PurchasingService.Services;

public class OrderService : IOrderService
{
    public Task<object> PlaceOrderAsync(Order order)
    {
        var supplier = SupplierStore.GetSupplierById(order.SupplierId);

        if (supplier is null)
        {
            throw new InvalidOperationException($"Supplier with id {order.SupplierId} was not found.");
        }

        var total = order.OrderDetails.Sum(detail => detail.Price * detail.Quantity);

        var response = new
        {
            Message = "Order placed successfully.",
            order.RequestId,
            order.SupplierId,
            order.Date,
            Total = total
        };

        return Task.FromResult<object>(response);
    }
}
