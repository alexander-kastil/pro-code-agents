using Microsoft.Extensions.AI;
using PurchasingService.Data;
using PurchasingService.Graph;
using PurchasingService.Models;

namespace PurchasingService.Services;

public class InquiryService : IInquiryService
{
    private readonly IOfferRandomizer _offerRandomizer;
    private readonly GraphHelper _graphHelper;
    private readonly IChatClient _chatClient;

    public InquiryService(IOfferRandomizer offerRandomizer, GraphHelper graphHelper, IChatClient chatClient)
    {
        _offerRandomizer = offerRandomizer ?? throw new ArgumentNullException(nameof(offerRandomizer));
        _graphHelper = graphHelper ?? throw new ArgumentNullException(nameof(graphHelper));
        _chatClient = chatClient ?? throw new ArgumentNullException(nameof(chatClient));
    }

    public async Task<OfferResponse> RequestOfferAsync(OfferRequest request)
    {
        if (request is null)
        {
            throw new ArgumentNullException(nameof(request));
        }

        if (request.RequestDetails is null || request.RequestDetails.Count == 0)
        {
            throw new ArgumentException("At least one product must be provided.", nameof(request));
        }

        var supplier = SupplierStore.GetSupplierById(request.SupplierId);

        if (supplier is null)
        {
            throw new InvalidOperationException($"Supplier with id {request.SupplierId} was not found.");
        }

        var offerLines = new List<OfferResponseDetail>(request.RequestDetails.Count);

        foreach (var productRequest in request.RequestDetails)
        {
            if (productRequest is null)
            {
                throw new ArgumentException("Product entries cannot be null.", nameof(request));
            }

            if (!_offerRandomizer.TryGetBasePrice(productRequest.Product, out _))
            {
                throw new ArgumentException($"Product '{productRequest.Product}' is not supported.", nameof(request));
            }

            offerLines.Add(_offerRandomizer.GenerateOffer(productRequest.Product, productRequest.RequestedQuantity));
        }

        var response = new OfferResponse
        {
            SupplierId = supplier.SupplierId,
            TransportationCost = _offerRandomizer.TransportationCost,
            Timestamp = DateTimeOffset.UtcNow,
            RequestDetails = offerLines,
            Email = request.Email?.Trim()
        };

        await ResponseHandler.TrySendOfferAsync(_graphHelper, _chatClient, response).ConfigureAwait(false);

        return response;
    }
}
