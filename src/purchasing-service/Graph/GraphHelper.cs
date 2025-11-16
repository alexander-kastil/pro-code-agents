using System.Collections.Generic;
using System.Threading.Tasks;
using Azure.Identity;
using Microsoft.Extensions.Options;
using Microsoft.Graph;
using Microsoft.Graph.Models;

namespace PurchasingService.Graph;

public class GraphHelper
{
    private static readonly string[] DefaultScopes = { "https://graph.microsoft.com/.default" };

    private readonly GraphOptions _options;

    public GraphHelper(IOptions<GraphOptions> options)
    {
        _options = options.Value;
    }

    public async Task SendMailAsync(string subject, string htmlMessage, IEnumerable<string> recipients)
    {
        var recipientList = new List<Recipient>();

        foreach (var address in recipients)
        {
            AddRecipient(recipientList, address);
        }

        var body = new ItemBody
        {
            ContentType = BodyType.Html,
            Content = htmlMessage,
        };

        var message = new Message
        {
            Subject = subject,
            Body = body,
            ToRecipients = recipientList,
        };

        await SendMailUsingGraphAsync(message).ConfigureAwait(false);
    }

    private async Task SendMailUsingGraphAsync(Message msg)
    {
        var credentials = new ClientSecretCredential(
            _options.TenantId,
            _options.ClientId,
            _options.ClientSecret);

        var graphClient = new GraphServiceClient(credentials, DefaultScopes);

        var requestBody = new Microsoft.Graph.Users.Item.SendMail.SendMailPostRequestBody
        {
            Message = msg,
            SaveToSentItems = false
        };

        await graphClient.Users[_options.MailSender].SendMail.PostAsync(requestBody).ConfigureAwait(false);
    }

    private static void AddRecipient(ICollection<Recipient> toRecipientsList, string address)
    {
        var emailAddress = new EmailAddress
        {
            Address = address,
        };

        var toRecipients = new Recipient
        {
            EmailAddress = emailAddress,
        };

        toRecipientsList.Add(toRecipients);
    }
}