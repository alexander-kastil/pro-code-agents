namespace SalesAgentApp;

public class AppConfig
{
    public string Model { get; set; } = string.Empty;
    public string Project_ConnectionString { get; set; } = string.Empty;
    public string DBName { get; set; } = string.Empty;
    public string AgentName { get; set; } = string.Empty;
    public string AllowedHosts { get; set; } = string.Empty;
    public ModelParams ModelParams { get; set; } = new();
}