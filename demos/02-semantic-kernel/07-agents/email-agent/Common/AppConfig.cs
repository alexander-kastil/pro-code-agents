public class Logging
{
    public LogLevel LogLevel { get; set; }
}

public class LogLevel
{
    public string Default { get; set; }
    public string Microsoft { get; set; }
    public string MicrosoftHostingLifetime { get; set; }
}

public class SemanticKernel
{
    public string Model { get; set; }
    public string Endpoint { get; set; }
    public string ApiKey { get; set; }
}

public class GraphCfg
{
    public string TenantId { get; set; }
    public string ClientId { get; set; }
    public string ClientSecret { get; set; }
    public string CacheLocation { get; set; }
    public Endpoints Endpoints { get; set; }
    public string ReturnUrl { get; set; }
    public string MailSender { get; set; }
}

public class Endpoints
{
    public string GraphApiUri { get; set; }
}

public class AppConfig
{
    public Logging Logging { get; set; }
    public SemanticKernel SemanticKernel { get; set; }
    public GraphCfg GraphCfg { get; set; }
    public string AllowedHosts { get; set; }
}
