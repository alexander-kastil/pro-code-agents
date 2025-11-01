namespace PurchasingService.Services;

public interface ISupplierService
{
    Task<List<Supplier>> GetAllSuppliersAsync();
    Task<Supplier?> GetSupplierByIdAsync(int id);
    Task<Supplier?> GetSupplierByNameAsync(string name);
    Task<List<Supplier>> GetSuppliersForProductAsync(string product);
}
