# C# Coding Standards

## Quick Reference

- Use `appsettings.json` for configuration (NOT environment variables or user secrets)
- XML documentation for public APIs
- PascalCase for classes/methods, camelCase for parameters
- async/await patterns for all I/O operations
- .NET 10.0 target framework

## Building and Testing

- Restore dependencies: `dotnet restore`
- Build: `dotnet build`
- Run: `dotnet run`
- **IMPORTANT**: Always use `appsettings.json` for configuration management
- Do NOT use environment variables or user secrets
- Configuration should be in `appsettings.json` and optionally `appsettings.Development.json`
- Use the dotnet cli for managing dependencies and running projects
