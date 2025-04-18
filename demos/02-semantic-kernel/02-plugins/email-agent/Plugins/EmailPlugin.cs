using System.ComponentModel;
using Microsoft.SemanticKernel;

public class EmailPlugin
{
    [KernelFunction("send_email")]
    [Description("Sends an email to a recipient.")]
    public Task SendEmailAsync(
        Kernel kernel,
        List<string> recipientEmails,
        string subject,
        string body
    )
    {
        Console.WriteLine("Sending email to recipients: " + string.Join(", ", recipientEmails));
        var config = new GraphCfg
        {
            ClientId = Environment.GetEnvironmentVariable("ClientId"),
            ClientSecret = Environment.GetEnvironmentVariable("ClientSecret"),
            TenantId = Environment.GetEnvironmentVariable("TenantId"),
            MailSender = Environment.GetEnvironmentVariable("MailSender")
        };
        GraphHelper.SendMail(subject, body, recipientEmails.ToArray(), config).Wait();

        return Task.CompletedTask;
    }
}