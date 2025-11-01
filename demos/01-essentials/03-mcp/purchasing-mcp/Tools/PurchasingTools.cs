using System.ComponentModel;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using PurchasingService.Models;
using PurchasingService.Services;

namespace PurchasingService.Tools;

/// <summary>
/// Provides purchasing management tools for the MCP server.
/// Enables AI agents to manage suppliers, request offers, and place orders.
/// </summary>
[McpServerToolType]
internal class PurchasingTools
{
    private readonly ISupplierService _supplierService;
    private readonly IInquiryService _inquiryService;
    private readonly IOrderService _orderService;
    private readonly ILogger<PurchasingTools> _logger;

    public PurchasingTools(
        ISupplierService supplierService,
        IInquiryService inquiryService,
        IOrderService orderService,
        ILogger<PurchasingTools> logger)
    {
        _supplierService = supplierService ?? throw new ArgumentNullException(nameof(supplierService));
        _inquiryService = inquiryService ?? throw new ArgumentNullException(nameof(inquiryService));
        _orderService = orderService ?? throw new ArgumentNullException(nameof(orderService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [McpServerTool]
    [Description("Retrieves the complete list of suppliers. It includes the supplierId, companyName information what suppliers can deliver which products in the availableProducts array.")]
    public async Task<SupplierCollection> GetSuppliers()
    {
        _logger.LogInformation("Fetching all suppliers");
        var suppliers = await _supplierService.GetAllSuppliersAsync();
        return new SupplierCollection { Suppliers = suppliers };
    }

    [McpServerTool]
    [Description("Requests an offer (inquiry) from a supplier for specified products. Returns offer details including pricing and availability.")]
    public async Task<string> RequestOffer(
        [Description("The unique identifier of the supplier: supplierId")] int supplierId,
        [Description("JSON array of products to request. Each item must have 'Product' (string) and 'RequestedQuantity' (integer). Example: [{\"Product\":\"Chai\",\"RequestedQuantity\":100}]")] string offerDetailsJson,
        [Description("Optional email address to send the offer to")] string? email = null)
    {
        if (string.IsNullOrWhiteSpace(offerDetailsJson))
        {
            throw new ArgumentException("Offer details must be provided.", nameof(offerDetailsJson));
        }

        List<OfferRequestDetail> offerDetails;
        try
        {
            offerDetails = JsonSerializer.Deserialize<List<OfferRequestDetail>>(offerDetailsJson)
                ?? throw new ArgumentException("Failed to parse offer details JSON.", nameof(offerDetailsJson));
        }
        catch (JsonException ex)
        {
            throw new ArgumentException($"Invalid JSON format for offer details: {ex.Message}", nameof(offerDetailsJson));
        }

        var request = new OfferRequest
        {
            SupplierId = supplierId,
            RequestDetails = offerDetails,
            Email = email
        };

        try
        {
            var response = await _inquiryService.RequestOfferAsync(request);
            return JsonSerializer.Serialize(response, new JsonSerializerOptions { WriteIndented = true });
        }
        catch (InvalidOperationException ex)
        {
            return $"Error: {ex.Message}";
        }
        catch (ArgumentException ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    [McpServerTool]
    [Description("Places an order with a supplier for specified products. Returns order confirmation with total cost.")]
    public async Task<string> PlaceOrder(
        [Description("A unique identifier for this order request")] string requestId,
        [Description("The unique identifier of the supplier")] int supplierId,
        [Description("The date of the order in ISO 8601 format (e.g., '2024-01-15T10:30:00Z')")] string orderDate,
        [Description("JSON array of order items. Each item must have 'productName' (string), 'price' (decimal), and 'quantity' (integer). Example: [{\"productName\":\"Chai\",\"price\":18.50,\"quantity\":100}]")] string orderDetailsJson)
    {
        _logger.LogInformation("Placing order for supplier {SupplierId}, request {RequestId}", supplierId, requestId);

        if (string.IsNullOrWhiteSpace(requestId))
        {
            throw new ArgumentException("Request ID must be provided.", nameof(requestId));
        }

        if (string.IsNullOrWhiteSpace(orderDetailsJson))
        {
            throw new ArgumentException("Order details must be provided.", nameof(orderDetailsJson));
        }

        if (!DateTime.TryParse(orderDate, out var parsedDate))
        {
            throw new ArgumentException("Order date must be a valid ISO 8601 date time string.", nameof(orderDate));
        }

        List<OrderDetail> orderDetails;
        try
        {
            orderDetails = JsonSerializer.Deserialize<List<OrderDetail>>(orderDetailsJson)
                ?? throw new ArgumentException("Failed to parse order details JSON.", nameof(orderDetailsJson));
        }
        catch (JsonException ex)
        {
            throw new ArgumentException($"Invalid JSON format for order details: {ex.Message}", nameof(orderDetailsJson));
        }

        var order = new Order
        {
            RequestId = requestId,
            SupplierId = supplierId,
            Date = parsedDate,
            OrderDetails = orderDetails
        };

        try
        {
            var response = await _orderService.PlaceOrderAsync(order);
            return JsonSerializer.Serialize(response, new JsonSerializerOptions { WriteIndented = true });
        }
        catch (InvalidOperationException ex)
        {
            return $"Error: {ex.Message}";
        }
    }
}
