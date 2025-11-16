using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.AI;
using PurchasingService.Data;
using PurchasingService.Graph;
using PurchasingService.Models;
using PurchasingService.Services;

namespace PurchasingService.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PurchasingController(IOfferRandomizer offerRandomizer, GraphHelper graphHelper, IChatClient chatClient) : ControllerBase
{
    [HttpPost("offer")]
    public async Task<ActionResult<OfferResponse>> GetOffer([FromBody] OfferRequest request)
    {
        if (request is null)
        {
            return BadRequest("Request payload is required.");
        }

        if (request.OfferDetails is null || request.OfferDetails.Count == 0)
        {
            return BadRequest("At least one product must be provided.");
        }

        var supplier = SupplierStore.GetSupplierById(request.SupplierId);

        if (supplier is null)
        {
            return NotFound($"Supplier with id {request.SupplierId} was not found.");
        }

        var offerLines = new List<OfferResponseDetail>(request.OfferDetails.Count);

        foreach (var productRequest in request.OfferDetails)
        {
            if (productRequest is null)
            {
                return BadRequest("Product entries cannot be null.");
            }

            if (!offerRandomizer.TryGetBasePrice(productRequest.ProductName, out _))
            {
                return BadRequest($"Product '{productRequest.ProductName}' is not supported.");
            }

            try
            {
                offerLines.Add(offerRandomizer.GenerateOffer(productRequest.ProductName, productRequest.RequestedAmount));
            }
            catch (ArgumentOutOfRangeException ex)
            {
                return BadRequest(ex.Message);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(ex.Message);
            }
        }

        var response = new OfferResponse
        {
            RequestId = request.RequestId,
            SupplierId = supplier.SupplierId,
            TransportationCost = offerRandomizer.TransportationCost,
            Timestamp = DateTimeOffset.UtcNow,
            OfferDetails = offerLines,
            Email = request.Email?.Trim()
        };

        if (await ResponseHandler.TrySendOfferAsync(graphHelper, chatClient, response).ConfigureAwait(false))
        {
            return Ok();
        }

        return Ok(response);
    }
}
