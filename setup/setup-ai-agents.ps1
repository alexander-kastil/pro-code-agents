d:\git-classes\m365-copilot\setup\setup-m365-copilot.ps1Write-Host "Installing VSCode & Git Related Software" -ForegroundColor yellow
Write-Host "Refresh Path Env - 1/6" -ForegroundColor yellow

winget install --id Microsoft.VisualStudioCode -e --accept-package-agreements --accept-source-agreements
winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
winget install --id GitHub.cli -e --accept-package-agreements --accept-source-agreements

# Install Software
Write-Host "Refresh Path Env - 2/6" -ForegroundColor yellow

winget install --id Microsoft.DotNet.SDK.9 -e --accept-package-agreements --accept-source-agreements
winget install --id OpenJS.NodeJS --version 22.11.0 -e --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.AzureCLI -e --accept-package-agreements --accept-source-agreements
winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements

# Refresh Path Env
Write-Host "Refresh Path Env - 3/6" -ForegroundColor yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Install Azure CLI Extensions without prompt
az config set extension.use_dynamic_install=yes_without_prompt

# Set NuGet Source
dotnet nuget add source https://api.nuget.org/v3/index.json -n nuget.org

# Intall VS Code Extensions
Write-Host "VS Code Extensions - 4/6" -ForegroundColor yellow

code --install-extension ms-dotnettools.csharp
code --install-extension ms-dotnettools.csdevkit
code --install-extension ms-vscode.powershell
code --install-extension ms-vscode.azurecli
code --install-extension GitHub.vscode-pull-request-github
code --install-extension redhat.vscode-yaml
code --install-extension mdickin.markdown-shortcuts
code --install-extension alex-pattison.theme-cobalt3
code --install-extension aliasadidev.nugetpackagemanagergui
code --install-extension humao.rest-client
code --install-extension github.copilot
code --install-extension teamsdevapp.vscode-adaptive-cards
code --install-extension teamsdevapp.ms-teams-vscode-extension
code --install-extension ms-azuretools.vscode-azurefunctions
code --install-extension ms-azuretools.vscode-bicep	
code --install-extension ms-copilotstudio.vscode-copilotstudio
code --install-extension teamsdevapp.vscode-ai-foundry
code --install-extension ms-graph.kiota

# Azurite Storage Emulator & Function Core Tools v4
npm install -g azure-functions-core-tools@4 --unsafe-perm true --force
npm install -g azurite

# Install Visual Studio Templates
Write-Host "Installing Visual Studio Templates" -ForegroundColor yellow
dotnet new install M365Advocacy.Teams.Templates
dotnet new install M365Advocacy.GraphConnectors.Templates

# Install Microsoft Graph PowerShell Module
Install-Module Microsoft.Graph -Scope CurrentUser

# Install Dev Tunnel CLI
winget install --id Microsoft.DevTunnelCLI -e --accept-package-agreements --accept-source-agreements

# Install Teams Toolkit CLI
npm install -g @microsoft/teamsapp-cli

# Install Kiota
dotnet tool install --global Microsoft.OpenApi.Kiota

# Finished Msg
Write-Host "Finished Software installation" -ForegroundColor yellow