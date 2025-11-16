
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Extensions.AI;
using PurchasingService.Graph;
using PurchasingService.Models;

public record PromptyTemplate(string SystemMessage, string UserTemplate);
