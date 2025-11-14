param(
    [string]$ResourceGroup = "rg-pro-code-agents-func",
    [string]$Location = "swedencentral",
    [string]$AppName = "YoutubeTranscript-demo",
    [string]$StorageName = "procodestorageacct",
    [string]$StorageConnectionString = "DefaultEndpointsProtocol=https;AccountName=procodestorageacct;AccountKey=V2Zp9uwbdT14k8mtcspa9Zmk9Rl3JIvI/XaDvuFfs52n3bmzuP/MF5OLWlBX1hy1++IVMmuX65Pq+AStcjNF0g==;EndpointSuffix=core.windows.net"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-AzCli() {
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        throw "Azure CLI 'az' is not installed or not on PATH. Install from https://aka.ms/azcli."
    }
}

function Ensure-Func() {
    if (-not (Get-Command func -ErrorAction SilentlyContinue)) {
        throw "Azure Functions Core Tools 'func' is not installed or not on PATH. Install v4 from https://aka.ms/azfunc-install."
    }
}

function Ensure-FlexLocationSupported([string]$loc) {
    try {
        $regions = az functionapp list-flexconsumption-locations -o tsv --query "[].name"
        if (-not ($regions -split "\r?\n" | Where-Object { $_ -eq $loc })) {
            Write-Host "Warning: '$loc' not in current Flex supported regions." -ForegroundColor Yellow
            Write-Host "Run: az functionapp list-flexconsumption-locations -o table" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Could not verify Flex regions (az CLI >=2.60 required). Proceeding..." -ForegroundColor Yellow
    }
}

function Ensure-Login() {
    try {
        $null = az account show --only-show-errors | Out-Null
    } catch {
        Write-Host "Not logged in. Opening browser..." -ForegroundColor Yellow
        az login | Out-Null
    }
}

function New-NameIfEmpty([string]$prefix, [int]$maxLen) {
    if ([string]::IsNullOrWhiteSpace($prefix)) { $prefix = "app" }
    $suffix = (Get-Random -Maximum 99999)
    $name = ($prefix + $suffix)
    if ($name.Length -gt $maxLen) { $name = $name.Substring(0, $maxLen) }
    return $name.ToLower()
}

Ensure-AzCli
Ensure-Func
Ensure-Login
Ensure-FlexLocationSupported -loc $Location

if ([string]::IsNullOrWhiteSpace($AppName)) {
    # Function app name must be globally unique
    $AppName = New-NameIfEmpty -prefix "youtube-transcript-" -maxLen 60
}

if ([string]::IsNullOrWhiteSpace($StorageName)) {
    if (-not [string]::IsNullOrWhiteSpace($StorageConnectionString)) {
        # Try to parse AccountName from connection string if provided
        $m = [regex]::Match($StorageConnectionString, 'AccountName=([^;]+)')
        if ($m.Success) {
            $StorageName = $m.Groups[1].Value
        }
    }
    if ([string]::IsNullOrWhiteSpace($StorageName)) {
        # Storage account: 3-24 lowercase alphanum, globally unique
        $StorageName = New-NameIfEmpty -prefix "youtubetranscript" -maxLen 24
    }
}

Write-Host "Using Resource Group: $ResourceGroup" -ForegroundColor Cyan
Write-Host "Using Location:       $Location" -ForegroundColor Cyan
Write-Host "Function App Name:    $AppName" -ForegroundColor Cyan
Write-Host "Storage Account:      $StorageName" -ForegroundColor Cyan

# Create or ensure resource group
az group create --name $ResourceGroup --location $Location --only-show-errors | Out-Null

# Create storage account if missing
try {
    $nameAvailable = az storage account check-name --name $StorageName --query "nameAvailable" -o tsv
} catch {
    $nameAvailable = "false"
}
if ($nameAvailable -eq "true") {
    az storage account create `
        --name $StorageName `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku Standard_LRS `
        --kind StorageV2 `
        --only-show-errors | Out-Null
} else {
    Write-Host "Using existing storage account: $StorageName" -ForegroundColor DarkCyan
}

# Create function app (Flex Consumption, Python 3.11)
$faExists = ""
try {
    $faExists = az functionapp show `
        --name $AppName `
        --resource-group $ResourceGroup `
        --query "name" -o tsv `
        --only-show-errors 2>$null
} catch {
    $faExists = ""
}
if ([string]::IsNullOrWhiteSpace($faExists)) {
    az functionapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --storage-account $StorageName `
        --flexconsumption-location $Location `
        --runtime python `
        --runtime-version 3.11 `
        --functions-version 4 `
        --only-show-errors | Out-Null
} else {
    Write-Host "Using existing function app: $AppName" -ForegroundColor DarkCyan
}

# Optional app settings
$appSettings = @("FUNCTIONS_EXTENSION_VERSION=~4")
if (-not [string]::IsNullOrWhiteSpace($StorageConnectionString)) { $appSettings += "AzureWebJobsStorage=$StorageConnectionString" }
if ($appSettings.Count -gt 0) {
    az functionapp config appsettings set `
        --name $AppName `
        --resource-group $ResourceGroup `
        --settings $appSettings `
        --only-show-errors | Out-Null
}

# Publish (remote build to match Linux runtime)
Write-Host "Publishing function app (remote build)..." -ForegroundColor Green
func azure functionapp publish $AppName --build remote --force

# Show function URL
Write-Host "Fetching function URL..." -ForegroundColor Green
$url = az functionapp function show -g $ResourceGroup -n $AppName --function-name get_transcription --query "invokeUrlTemplate" -o tsv 2>$null
if ([string]::IsNullOrWhiteSpace($url)) {
    $base = az functionapp show -g $ResourceGroup -n $AppName --query "defaultHostName" -o tsv
    if ($base) { $url = "https://$base/api/get_transcription" }
}
Write-Host "Function URL: $url" -ForegroundColor Yellow
