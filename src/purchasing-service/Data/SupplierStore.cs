using System.Collections.ObjectModel;

namespace PurchasingService.Data;

public static class SupplierStore
{
    private static readonly IReadOnlyList<Supplier> Suppliers = new ReadOnlyCollection<Supplier>(
        new List<Supplier>
        {
            new()
            {
                SupplierId = 1,
                CompanyName = "Exotic Liquids",
                ContactName = "Charlotte Cooper",
                ContactTitle = "Purchasing Manager",
                City = "London",
                Region = string.Empty,
                Country = "UK",
                PostalCode = "EC1A 4SB",
                Phone = "(171) 555-2222",
                EMail = "charlotte.cooper@exoticliquids.example",
                Address = "49 Gilbert St",
                HomePage = "https://exoticliquids.example"
            },
            new()
            {
                SupplierId = 2,
                CompanyName = "New Orleans Cajun Delights",
                ContactName = "Shelley Burke",
                ContactTitle = "Order Administrator",
                City = "New Orleans",
                Region = "LA",
                Country = "USA",
                PostalCode = "70116",
                Phone = "(100) 555-4822",
                EMail = "shelley.burke@nocd.example",
                Address = "P.O. Box 78934",
                HomePage = "https://nocd.example"
            },
            new()
            {
                SupplierId = 3,
                CompanyName = "Grandma Kelly's Homestead",
                ContactName = "Regina Murphy",
                ContactTitle = "Sales Representative",
                City = "Ann Arbor",
                Region = "MI",
                Country = "USA",
                PostalCode = "48103",
                Phone = "(313) 555-5735",
                EMail = "regina.murphy@gkh.example",
                Address = "707 Oxford Rd.",
                HomePage = "https://gkh.example"
            },
            new()
            {
                SupplierId = 4,
                CompanyName = "Schnitzel Express",
                ContactName = "Franz Bauer",
                ContactTitle = "Operations Lead",
                City = "Vienna",
                Region = string.Empty,
                Country = "Austria",
                PostalCode = "1010",
                Phone = "+43 1 555 0199",
                EMail = "franz.bauer@schnitzel-express.example",
                Address = "Ringstrasse 12",
                HomePage = "https://schnitzel-express.example"
            }
        });

    public static IReadOnlyList<Supplier> GetSuppliers() => Suppliers;

    public static Supplier? GetSupplierById(int supplierId) =>
        Suppliers.FirstOrDefault(s => s.SupplierId == supplierId);

    public static Supplier? GetSupplierByName(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            return null;
        }

        return Suppliers.FirstOrDefault(
            s => string.Equals(s.CompanyName, name, StringComparison.OrdinalIgnoreCase));
    }
}
