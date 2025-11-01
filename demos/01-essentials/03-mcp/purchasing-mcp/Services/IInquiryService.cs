using PurchasingService.Models;

namespace PurchasingService.Services;

public interface IInquiryService
{
    Task<OfferResponse> RequestOfferAsync(OfferRequest request);
}
