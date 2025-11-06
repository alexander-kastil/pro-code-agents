using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace sk_ai_agent;

public class EmailPlugin(GraphCfg config)
{
    [KernelFunction("send_email")]
    [Description("Sends an email to a recipient.")]
    public async Task SendEmailAsync(
        Kernel kernel,
        List<string> recipientEmails,
        string subject,
        string body
    )
    {
        Console.WriteLine("Sending email to recipients: " + string.Join(", ", recipientEmails));
        GraphHelper graphHelper = new GraphHelper(config);
        await graphHelper.SendMail(subject, body, recipientEmails.ToArray());
    }
}
