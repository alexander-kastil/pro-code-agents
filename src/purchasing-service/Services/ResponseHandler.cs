using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Extensions.AI;
using PurchasingService.Data;
using PurchasingService.Graph;
using PurchasingService.Models;

namespace PurchasingService.Services;

public static class ResponseHandler
{
    public static async Task<bool> TrySendOfferAsync(GraphHelper graphHelper, IChatClient chatClient, OfferResponse response)
    {
        ArgumentNullException.ThrowIfNull(graphHelper);
        ArgumentNullException.ThrowIfNull(chatClient);
        ArgumentNullException.ThrowIfNull(response);

        if (string.IsNullOrWhiteSpace(response.Email))
        {
            return false;
        }

        var sanitizedEmail = response.Email.Trim();

        var subject = $"Offer {response.RequestId}";
        var body = await BuildEmailBodyAsync(chatClient, response).ConfigureAwait(false);

        await graphHelper.SendMailAsync(subject, body, new[] { sanitizedEmail }).ConfigureAwait(false);

        return true;
    }

    private static async Task<string> BuildEmailBodyAsync(IChatClient chatClient, OfferResponse response)
    {
        var details = response.OfferDetails ?? Array.Empty<OfferResponseDetail>();
        var supplier = SupplierStore.GetSupplierById(response.SupplierId);
        var currencyCulture = GetCurrencyCulture(supplier);
        var detailLines = details.Select(detail =>
        {
            var total = detail.OfferedAmount * detail.OfferedPrice;
            var statusSuffix = detail.IsAvailable ? string.Empty : "; Status: Unavailable";
            return $"- Product: {detail.ProductName}; Requested: {detail.RequestedAmount}; Offered: {detail.OfferedAmount}; Price: {FormatCurrency(detail.OfferedPrice, currencyCulture)}; Total: {FormatCurrency(total, currencyCulture)}; Delivery: {detail.DeliveryDurationDays} days{statusSuffix}";
        });
        var detailsText = detailLines.Any() ? string.Join(Environment.NewLine, detailLines) : "No offer lines present.";
        var unavailableNotice = BuildUnavailableNotice(details);

        var supplierCompany = supplier?.CompanyName ?? $"Supplier {response.SupplierId}";
        var supplierAddress = FormatSupplierAddress(supplier);

        try
        {
            var promptyContent = await LoadPromptyFileAsync().ConfigureAwait(false);
            var prompty = ParsePromptyFile(promptyContent);
            var userMessage = ReplaceTemplateVariables(prompty.UserTemplate, new Dictionary<string, string>
            {
                ["requestId"] = response.RequestId,
                ["supplierId"] = response.SupplierId.ToString(CultureInfo.InvariantCulture),
                ["supplierCompany"] = supplierCompany,
                ["supplierAddress"] = supplierAddress,
                ["transportationCost"] = FormatCurrency(response.TransportationCost, currencyCulture),
                ["timestamp"] = response.Timestamp.ToString("u", CultureInfo.InvariantCulture),
                ["details"] = detailsText,
                ["unavailableNotice"] = unavailableNotice
            });

            var messages = new List<ChatMessage>
            {
                new(ChatRole.System, prompty.SystemMessage),
                new(ChatRole.User, userMessage)
            };

            var result = await chatClient.CompleteAsync(messages).ConfigureAwait(false);
            var generated = result.Message.Text;
            if (!string.IsNullOrWhiteSpace(generated))
            {
                return generated;
            }
        }
        catch (Exception)
        {
            // Intentionally swallow exceptions and fall back to deterministic formatting.
        }

        // Fallback deterministic formatting if AI generation fails or exception occurs
        var fallbackDetails = response.OfferDetails ?? Array.Empty<OfferResponseDetail>();
        var fallbackDetailBuilder = new StringBuilder();
        foreach (var detail in fallbackDetails)
        {
            var total = detail.OfferedAmount * detail.OfferedPrice;
            var line = $"- Product: {detail.ProductName}; Requested: {detail.RequestedAmount}; Offered: {detail.OfferedAmount}; Price: {FormatCurrency(detail.OfferedPrice, currencyCulture)}; Total: {FormatCurrency(total, currencyCulture)}; Delivery: {detail.DeliveryDurationDays} days";
            fallbackDetailBuilder.AppendLine(line);
        }

        var fallbackDetailsText = fallbackDetailBuilder.Length == 0 ? "No offer lines present." : fallbackDetailBuilder.ToString();
        var fallbackUnavailableNotice = BuildUnavailableNotice(fallbackDetails);

        var fallbackSections = new List<string>
        {
            $"Offer {response.RequestId} from supplier {response.SupplierId} at {response.Timestamp:u}",
            $"Transportation Cost: {FormatCurrency(response.TransportationCost, currencyCulture)}",
            "Details:",
            fallbackDetailsText
        };

        if (!string.IsNullOrWhiteSpace(fallbackUnavailableNotice))
        {
            fallbackSections.Add(fallbackUnavailableNotice);
        }

        fallbackSections.Add(string.Empty);
        fallbackSections.Add("Supplier:");
        fallbackSections.Add(supplierCompany);
        fallbackSections.Add(supplierAddress);

        return string.Join(Environment.NewLine, fallbackSections);
    }

    private static async Task<string> LoadPromptyFileAsync()
    {
        var promptyPath = Path.Combine(AppContext.BaseDirectory, "Prompts", "EmailGeneration.prompty");
        return await File.ReadAllTextAsync(promptyPath).ConfigureAwait(false);
    }

    private static PromptyTemplate ParsePromptyFile(string promptyContent)
    {
        var systemMatch = Regex.Match(promptyContent, @"system:\s*\r?\n(.*?)(?=\r?\n\s*user:)", RegexOptions.Singleline);
        var userMatch = Regex.Match(promptyContent, @"user:\s*\r?\n(.*?)$", RegexOptions.Singleline);

        var systemMessage = systemMatch.Success ? systemMatch.Groups[1].Value.Trim() : string.Empty;
        var userTemplate = userMatch.Success ? userMatch.Groups[1].Value.Trim() : string.Empty;

        return new PromptyTemplate(systemMessage, userTemplate);
    }

    private static string ReplaceTemplateVariables(string template, Dictionary<string, string> variables)
    {
        var result = template;
        foreach (var kvp in variables)
        {
            result = result.Replace($"{{{{{kvp.Key}}}}}", kvp.Value);
        }
        return result;
    }

    private static string FormatSupplierAddress(Supplier? supplier)
    {
        if (supplier is null)
        {
            return "Address not available.";
        }

        var parts = new List<string>
        {
            supplier.Address,
            CombineCityRegionPostal(supplier.City, supplier.Region, supplier.PostalCode),
            supplier.Country
        };

        return string.Join("\n", parts.Where(part => !string.IsNullOrWhiteSpace(part)));
    }

    private static string CombineCityRegionPostal(string city, string region, string postalCode)
    {
        var segments = new List<string>();
        if (!string.IsNullOrWhiteSpace(city))
        {
            segments.Add(city);
        }

        if (!string.IsNullOrWhiteSpace(region))
        {
            segments.Add(region);
        }

        if (!string.IsNullOrWhiteSpace(postalCode))
        {
            segments.Add(postalCode);
        }

        return string.Join(", ", segments);
    }

    private static CultureInfo GetCurrencyCulture(Supplier? supplier)
    {
        if (supplier is null)
        {
            return CultureInfo.CurrentCulture;
        }

        return supplier.Country switch
        {
            "USA" => CultureInfo.GetCultureInfo("en-US"),
            "UK" => CultureInfo.GetCultureInfo("en-GB"),
            "Austria" => CultureInfo.GetCultureInfo("de-AT"),
            _ => CultureInfo.CurrentCulture
        };
    }

    private static string FormatCurrency(decimal value, CultureInfo culture)
    {
        return value.ToString("C", culture);
    }

    private static string BuildUnavailableNotice(IEnumerable<OfferResponseDetail> details)
    {
        var unavailableProducts = details
            .Where(detail => !detail.IsAvailable)
            .Select(detail => detail.ProductName)
            .Where(name => !string.IsNullOrWhiteSpace(name))
            .ToList();

        if (unavailableProducts.Count == 0)
        {
            return string.Empty;
        }

        if (unavailableProducts.Count == 1)
        {
            return $"Note: {unavailableProducts[0]} is currently unavailable for delivery.";
        }

        var productList = string.Join(", ", unavailableProducts);
        return $"Note: {productList} are currently unavailable for delivery.";
    }
}