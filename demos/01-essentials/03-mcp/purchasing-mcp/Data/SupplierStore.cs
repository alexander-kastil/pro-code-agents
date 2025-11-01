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
                CompanyName = "Wiener Feinkost GmbH",
                ContactName = "Anna Stöger",
                ContactTitle = "Einkaufsleiterin",
                City = "Vienna",
                Region = "Wien",
                Country = "Austria",
                PostalCode = "1010",
                Phone = "+43 1 234 5678",
                EMail = "anna.stoeger@wiener-feinkost.at",
                Address = "Graben 21",
                HomePage = "https://wiener-feinkost.at",
                AvailableProducts = new List<string>
                {
                    "Wiener Schnitzel",
                    "Germknoedel",
                    "Kaiserschmarrn",
                }
            },
            new()
            {
                SupplierId = 2,
                CompanyName = "Muenchner Gewuerze GmbH",
                ContactName = "Juergen Mueller",
                ContactTitle = "Verkaufsleiter",
                City = "Muenchen",
                Region = "Bayern",
                Country = "Germany",
                PostalCode = "80331",
                Phone = "+49 89 123456",
                EMail = "info@muenchner-gewuerze.de",
                Address = "Marienplatz 1",
                HomePage = "https://muenchner-gewuerze.de",
                AvailableProducts = new List<string>
                {
                    "Weisswurst mit Senf",
                    "Curry Wurst",
                    "Schweinshaxe mit Sauerkraut",
                }
            },
            new()
             {
                SupplierId = 3,
                CompanyName = "Partenope Gastronomia S.r.l.",
                ContactName = "Antonio Bianchi",
                ContactTitle = "Manager Operativo",
                City = "Napoli",
                Region = "Campania",
                Country = "Italy",
                PostalCode = "80132",
                Phone = "+39 081 555 7890",
                EMail = "antonio.bianchi@partenope.it",
                Address = "Corso Umberto I 15",
                HomePage = "https://pizza-napoli.it",
                AvailableProducts = new List<string>
                {
                    "Pizza Napoli",
                    "Arancini Napoletana"
                }
            },
            new()
            {
                SupplierId = 4,
                CompanyName = "Same, same but different Foods Co., Ltd.",
                ContactName = "Alek Kastil",
                ContactTitle = "Operations Manager",
                City = "Bangkok",
                Region = string.Empty,
                Country = "Thailand",
                PostalCode = "10100",
                Phone = "+66 2 123 4567",
                EMail = "alek.kastil@bangkokfoods.th",
                Address = "Sukhumvit Rd. 45",
                HomePage = "https://bangkokfoods.th",
                AvailableProducts = new List<string>
                {
                    "Pad Ka Prao",
                    "Massaman Curry",
                    "Green Curry",
                }
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
