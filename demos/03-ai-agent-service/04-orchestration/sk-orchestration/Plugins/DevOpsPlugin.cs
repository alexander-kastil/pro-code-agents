using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;

namespace SKOrchestration;

public class DevopsPlugin
{
    /// <summary>
    /// A plugin that performs developer operation tasks.
    /// </summary>

    private void AppendToLogFile(string filepath, string content)
    {
        File.AppendAllText(filepath, "\n" + content.Trim());
    }

    [KernelFunction(Description = "A function that restarts the named service")]
    public string RestartService(string serviceName = "", string logfile = "")
    {
        var logEntries = new[]
        {
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] ALERT  DevopsAssistant: Multiple failures detected in {serviceName}. Restarting service.",
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] INFO  {serviceName}: Restart initiated.",
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] INFO  {serviceName}: Service restarted successfully."
        };

        var logMessage = string.Join("\n", logEntries);
        AppendToLogFile(logfile, logMessage);

        return $"Service {serviceName} restarted successfully.";
    }

    [KernelFunction(Description = "A function that rollsback the transaction")]
    public string RollbackTransaction(string logfile = "")
    {
        var logEntries = new[]
        {
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] ALERT  DevopsAssistant: Transaction failure detected. Rolling back transaction batch.",
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] INFO   TransactionProcessor: Rolling back transaction batch.",
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] INFO   Transaction rollback completed successfully."
        };

        var logMessage = string.Join("\n", logEntries);
        AppendToLogFile(logfile, logMessage);

        return "Transaction rolled back successfully.";
    }
    [KernelFunction(Description = "A function that redeploys the named resource")]
    public string RedeployResource(string resourceName = "", string logfile = "")
    {
        var logEntries = new[]
        {
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] ALERT  DevopsAssistant: Resource deployment failure detected in '{resourceName}'. Redeploying resource.",
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] INFO   DeploymentManager: Redeployment request submitted.",
            $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] INFO   DeploymentManager: Service successfully redeployed, resource '{resourceName}' created successfully."
        };

        var logMessage = string.Join("\n", logEntries);
        AppendToLogFile(logfile, logMessage);

        return $"Resource '{resourceName}' redeployed successfully.";
    }
}