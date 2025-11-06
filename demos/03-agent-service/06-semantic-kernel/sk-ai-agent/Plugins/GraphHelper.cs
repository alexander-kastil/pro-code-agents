using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Azure.Identity;
using Microsoft.Graph;
using Microsoft.Graph.Models;

namespace sk_ai_agent;

public class GraphHelper
{
    private readonly GraphCfg config;
    private readonly GraphServiceClient graphClient;

    public GraphHelper(GraphCfg config)
    {
        this.config = config;

        var credentials = new ClientSecretCredential(
            config.TenantId,
            config.ClientId,
            config.ClientSecret
        );

        this.graphClient = new GraphServiceClient(credentials, new[] { "https://graph.microsoft.com/.default" });
    }

    public async Task SendMail(string subject, string message, string[] recipients)
    {
        var recipientList = new List<Recipient>();

        foreach (var r in recipients)
        {
            AddRecipient(recipientList, r);
        }

        var body = new ItemBody
        {
            ContentType = BodyType.Html,
            Content = message,
        };

        var emailMessage = new Message
        {
            Subject = subject,
            Body = body,
            ToRecipients = recipientList,
        };

        await SendMailUsingGraphAsync(emailMessage);
    }

    private async Task SendMailUsingGraphAsync(Message msg)
    {
        var requestBody = new Microsoft.Graph.Users.Item.SendMail.SendMailPostRequestBody
        {
            Message = msg,
            SaveToSentItems = false
        };

        await this.graphClient.Users[this.config.MailSender].SendMail.PostAsync(requestBody);
    }

    private void AddRecipient(List<Recipient> toRecipientsList, string r)
    {
        var emailAddress = new EmailAddress
        {
            Address = r,
        };

        var toRecipients = new Recipient
        {
            EmailAddress = emailAddress,
        };

        toRecipientsList.Add(toRecipients);
    }
}

