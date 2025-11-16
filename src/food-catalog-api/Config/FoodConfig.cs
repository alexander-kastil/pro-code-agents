using Microsoft.Extensions.Configuration;

namespace FoodApp
{
    public class FoodConfig
    {
        public Azure Azure { get; set; }
        public ApplicationInsights ApplicationInsights { get; set; }
        public ConnectionStrings ConnectionStrings { get; set; }
        public AppConfig App { get; set; }
        public FeatureManagement FeatureManagement { get; set; }
        public Logging Logging { get; set; }
    }

    public class AppConfig
    {
        public string Title { get; set; }
        public bool AuthEnabled { get; set; }
    }

    public class Azure
    {
        public string TenantId { get; set; }
        public string ClientId { get; set; }
        public string Instance { get; set; }
        [ConfigurationKeyName("cacheLocation")]
        public string CacheLocation { get; set; }
        public string AppConfigurationCS { get; set; }
        public string KeyVault { get; set; }
        public string EventGridKey { get; set; }
        public string EventGridEP { get; set; }
    }

    public class ApplicationInsights
    {
        public string ConnectionString { get; set; }
    }

    public class ConnectionStrings
    {
        public string DefaultDatabase { get; set; }
    }

    public class FeatureManagement
    {
        public bool PublishEvents { get; set; }
        public bool UseKeyVaultWithMI { get; set; }
        public bool UseHealthChecks { get; set; }
        public bool UseApplicationInsights { get; set; }
    }

    public class LogLevel
    {
        public string Default { get; set; }
        public string Microsoft { get; set; }

        [ConfigurationKeyName("Microsoft.Hosting.Lifetime")]
        public string MicrosoftHostingLifetime { get; set; }
    }

    public class Logging
    {
        public LogLevel LogLevel { get; set; }
    }
}