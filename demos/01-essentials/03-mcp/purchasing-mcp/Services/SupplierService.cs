using PurchasingService.Data;

namespace PurchasingService.Services;

public class SupplierService : ISupplierService
{
    public Task<List<Supplier>> GetAllSuppliersAsync()
    {
        return Task.FromResult(SupplierStore.GetSuppliers().ToList());
    }

    public Task<Supplier?> GetSupplierByIdAsync(int id)
    {
        return Task.FromResult(SupplierStore.GetSupplierById(id));
    }

    public Task<Supplier?> GetSupplierByNameAsync(string name)
    {
        return Task.FromResult(SupplierStore.GetSupplierByName(name));
    }

    public Task<List<Supplier>> GetSuppliersForProductAsync(string product)
    {
        var matches = SupplierStore.GetSuppliers()
            .Where(s => s.AvailableProducts.Any(p => string.Equals(p, product, StringComparison.OrdinalIgnoreCase)))
            .ToList();

        return Task.FromResult(matches);
    }
}
