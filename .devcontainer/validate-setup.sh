#!/usr/bin/env bash

# Validation script for devcontainer setup
# This script verifies that all required tools and configurations are properly installed

set -euo pipefail

echo "=========================================="
echo "Devcontainer Setup Validation"
echo "=========================================="
echo ""

ERRORS=0

# Function to check if a command exists
check_command() {
    local cmd=$1
    local name=${2:-$cmd}
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "✓ $name found: $($cmd --version 2>&1 | head -n 1)"
        return 0
    else
        echo "✗ $name not found"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check version output
check_version() {
    local cmd=$1
    local name=$2
    if $cmd >/dev/null 2>&1; then
        echo "✓ $name installed"
        return 0
    else
        echo "✗ $name not installed"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

echo "--- Core Development Tools ---"
check_command dotnet ".NET SDK"
check_command node "Node.js"
check_command npm "npm"
check_command python "Python"
check_command pwsh "PowerShell Core"

echo ""
echo "--- Cloud & Azure Tools ---"
check_command az "Azure CLI"
check_command azd "Azure Developer CLI"
check_command func "Azure Functions Core Tools"
check_command azurite "Azurite"
check_command gh "GitHub CLI"

echo ""
echo "--- Microsoft 365 & Teams Tools ---"
if npm list -g @microsoft/m365agentstoolkit-cli >/dev/null 2>&1; then
    echo "✓ Microsoft 365 Agents Toolkit CLI installed"
else
    echo "✗ Microsoft 365 Agents Toolkit CLI not found"
    ERRORS=$((ERRORS + 1))
fi

if npm list -g @microsoft/m365agentsplayground >/dev/null 2>&1; then
    echo "✓ Microsoft 365 Agents Playground installed"
else
    echo "✗ Microsoft 365 Agents Playground not found"
    ERRORS=$((ERRORS + 1))
fi

if npm list -g @microsoft/teams.cli >/dev/null 2>&1; then
    echo "✓ Teams CLI installed"
else
    echo "✗ Teams CLI not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "--- .NET Global Tools ---"
if dotnet tool list -g | grep -q "Microsoft.OpenApi.Kiota"; then
    echo "✓ Kiota (.NET global tool) installed"
else
    echo "✗ Kiota not found"
    ERRORS=$((ERRORS + 1))
fi

if dotnet tool list -g | grep -q "microsoft.dotnet-interactive"; then
    echo "✓ .NET Interactive installed"
else
    echo "✗ .NET Interactive not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "--- Jupyter Support ---"
check_command jupyter "Jupyter"

echo ""
echo "Checking Jupyter kernels..."
if jupyter kernelspec list | grep -q "python3"; then
    echo "✓ Python 3 kernel found"
else
    echo "✗ Python 3 kernel not found"
    ERRORS=$((ERRORS + 1))
fi

if jupyter kernelspec list | grep -q ".net-csharp"; then
    echo "✓ .NET C# kernel found"
else
    echo "✗ .NET C# kernel not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "--- PowerShell Modules ---"
# Check both modules in a single PowerShell session
PS_MODULES_CHECK=$(pwsh -NoLogo -NoProfile -Command "
    \$modules = @('Microsoft.Graph', 'Microsoft.Online.SharePoint.PowerShell')
    \$results = @{}
    foreach (\$module in \$modules) {
        \$results[\$module] = (Get-Module -ListAvailable \$module) -ne \$null
    }
    \$results | ConvertTo-Json
" 2>/dev/null)

if echo "$PS_MODULES_CHECK" | grep -q '"Microsoft.Graph".*true'; then
    echo "✓ Microsoft.Graph PowerShell module installed"
else
    echo "✗ Microsoft.Graph PowerShell module not found"
    ERRORS=$((ERRORS + 1))
fi

if echo "$PS_MODULES_CHECK" | grep -q '"Microsoft.Online.SharePoint.PowerShell".*true'; then
    echo "✓ Microsoft.Online.SharePoint.PowerShell module installed"
else
    echo "✗ Microsoft.Online.SharePoint.PowerShell module not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "--- Optional Tools ---"
if command -v devtunnel >/dev/null 2>&1; then
    echo "✓ Dev Tunnels CLI installed (optional)"
else
    echo "ℹ Dev Tunnels CLI not installed (optional, installed in post-create)"
fi

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All required tools are installed!"
    echo "=========================================="
    exit 0
else
    echo "❌ $ERRORS error(s) found!"
    echo "=========================================="
    exit 1
fi
