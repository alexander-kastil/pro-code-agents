using Microsoft.AspNetCore.Mvc;

using PurchasingService.Data;

namespace PurchasingService.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SuppliersController : ControllerBase
{
    [HttpGet]
    public ActionResult<IEnumerable<Supplier>> GetSuppliers()
    {
        return Ok(SupplierStore.GetSuppliers());
    }

    [HttpGet("{id:int}")]
    public ActionResult<Supplier> GetSupplierById(int id)
    {
        var supplier = SupplierStore.GetSupplierById(id);
        return supplier is null ? NotFound() : Ok(supplier);
    }

    [HttpGet("by-name/{name}")]
    public ActionResult<Supplier> GetSupplierByName(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            return BadRequest("Name must be provided.");
        }

        var supplier = SupplierStore.GetSupplierByName(name);

        return supplier is null ? NotFound() : Ok(supplier);
    }
}
