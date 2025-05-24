#!/bin/bash
# filepath: /workspace/.devcontainer/post-create.sh

set -e  # Exit on any error

echo "Post-creation setup starting..."

# Configure Azure CLI (already installed via devcontainer features)
echo "Configuring Azure CLI..."
az config set extension.use_dynamic_install=yes_without_prompt

# Install Kiota (.NET is already available via devcontainer features)
echo "Installing Kiota..."
dotnet tool install --global Microsoft.OpenApi.Kiota

# Verify installations
echo "Verifying installations..."
echo "Azure CLI version: $(az --version | head -n1)"
echo "Azure Functions Core Tools version: $(func --version)"
echo "Azurite version: $(azurite --version)"
echo "Teams Toolkit CLI version: $(teamsapp --version)"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo ".NET version: $(dotnet --version)"
echo "Kiota version: $(kiota --version)"

echo "Post-creation setup completed successfully!"