using Microsoft.AspNetCore.Mvc;
using PurchasingService.Models;
using PurchasingService.Services;

namespace PurchasingService.Controllers;

[ApiController]
[Route("[controller]")]
public class InquiryController : ControllerBase
{
    private readonly IInquiryService _inquiryService;

    public InquiryController(IInquiryService inquiryService)
    {
        _inquiryService = inquiryService ?? throw new ArgumentNullException(nameof(inquiryService));
    }

    [HttpPost("requestOffer")]
    public async Task<ActionResult<OfferResponse>> GetOffer([FromBody] OfferRequest request)
    {
        if (request is null)
        {
            return BadRequest("Request payload is required.");
        }

        if (request.RequestDetails is null || request.RequestDetails.Count == 0)
        {
            return BadRequest("At least one product must be provided.");
        }

        try
        {
            var response = await _inquiryService.RequestOfferAsync(request);
            return Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return NotFound(ex.Message);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
    }
}
