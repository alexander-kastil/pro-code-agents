# Microsoft Foundry Deployment

This demo demonstrates how to deploy Azure AI Foundry infrastructure using Azure Developer CLI (azd) and Bicep templates.

## Contents

The infrastructure files are located at the **workspace root** (`d:\git-classes\pro-code-agents\`):

- `infra/main.bicep` - Main Bicep infrastructure template
- `infra/get-keys.sh` - Script to retrieve Azure resource keys and generate configuration files
- `azure.yaml` - Azure Developer CLI configuration

## Prerequisites

- Azure CLI installed and authenticated (`az login`)
- Azure Developer CLI (azd) installed ([installation guide](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd))
- An active Azure subscription

## Deployment

### 1. Initialize Azure Developer CLI

From the **workspace root** (`d:\git-classes\pro-code-agents\`):

```powershell
# Create a new environment (will prompt for Azure location)
azd env new dev-swedencentral

# Optional: Set service principal if needed for RBAC
azd env set SERVICE_PRINCIPAL_OBJECT_ID <your-service-principal-object-id>
```

### 2. Deploy Infrastructure

```powershell
# Deploy all resources from infra/main.bicep
azd up
```

This deploys:

- Azure AI Foundry Resource (CognitiveServices account)
- Azure AI Foundry Project (hubless architecture)
- Azure AI Search
- Storage Account
- Log Analytics Workspace
- Application Insights
- Model Deployments (gpt-4o-mini, text-embedding-ada-002)
- Proper RBAC role assignments

**Note:** This uses the modern **Foundry project** architecture without a hub.

### 3. Deploy to Multiple Regions

To deploy the same infrastructure to different regions:

```powershell
# Create a new environment for production in West Europe
azd env new prod-westeurope

# Note: Update infra/main.bicep @allowed location if targeting non-swedencentral regions

# Deploy to the new environment
azd up

# Switch between environments
azd env list
azd env select dev-swedencentral
```

### 4. Retrieve Configuration Keys

### 4. Retrieve Configuration Keys

After successful deployment, run `get-keys.sh` to extract connection strings and keys from deployed resources.

#### Running the Script

From the **workspace root** (`d:\git-classes\pro-code-agents\`):

```bash
# Navigate to infra directory
cd infra

# Interactive mode (prompts for resource group)
./get-keys.sh

# Or with resource group parameter
./get-keys.sh --resource-group <your-resource-group-name>
```

**Finding Your Resource Group Name:**

```powershell
# List all environments
azd env list

# Get environment values (including resource group)
azd env get-values
```

The resource group follows the pattern: `rg-<app-name>-<environment-name>`

#### Generated Files

The script creates configuration files at the **workspace root** (`d:\git-classes\pro-code-agents\`):

1. **`.env`** - Environment variables file for Python projects and demos

   - Contains all Azure resource connection strings and keys
   - Format: `KEY="value"`
   - Used by Python demos in this repository
   - ⚠️ **Already in `.gitignore` - never commit this file**

2. **`appsettings.json`** - Configuration file for C# .NET projects
   - Contains structured configuration under `AzureConfig` section
   - Format: JSON with nested configuration
   - Used by .NET demos in this repository
   - ⚠️ **Contains secrets - do not commit to git**

#### Configuration Variables

The generated files include:

**Storage Account:**

- `STORAGE_ACCOUNT_NAME` / `AZURE_STORAGE_ACCOUNT_NAME`
- `STORAGE_ACCOUNT_KEY` / `AZURE_STORAGE_ACCOUNT_KEY`
- `STORAGE_CONNECTION_STRING` / `AZURE_STORAGE_CONNECTION_STRING`
- `STORAGE_CONTAINER_NAME`

**Azure AI Search:**

- `SEARCH_SERVICE_NAME`
- `SEARCH_SERVICE_ENDPOINT`
- `SEARCH_ADMIN_KEY`

**Azure AI Foundry:**

- `AI_FOUNDRY_HUB_NAME` (actually the Foundry resource name, not a hub)
- `AI_FOUNDRY_PROJECT_NAME`
- `AI_FOUNDRY_ENDPOINT`
- `AI_FOUNDRY_KEY`
- `AI_FOUNDRY_HUB_ENDPOINT` (Foundry resource portal URL)
- `AI_FOUNDRY_PROJECT_ENDPOINT`
- `PROJECT_ENDPOINT`

**Azure OpenAI (compatibility):**

- `AZURE_OPENAI_SERVICE_NAME`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_AI_MODELS_ENDPOINT`
- `AZURE_AI_MODELS_KEY`

**Other Resources:**

- `LOG_ANALYTICS_WORKSPACE_NAME`
- `EMBEDDINGS_MODEL`
- `MODEL_DEPLOYMENT_NAME`
- `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_CONNECTION_STRING` (if Cosmos DB is deployed)
- `ACR_NAME`, `ACR_USERNAME`, `ACR_PASSWORD` (if Container Registry is deployed)

## Managing Deployments

### View Deployed Resources

```powershell
# List all environments
azd env list

# Show current environment details
azd env show

# View all environment variables
azd env get-values
```

### Update Deployment

```powershell
# Make changes to infra/main.bicep, then redeploy
azd up
```

### Tear Down Resources

```powershell
# Remove all Azure resources (does not delete local files)
azd down

# Remove resources and purge soft-deleted items
azd down --purge
```

### Reset for Fresh Deployment

To completely reset and redeploy:

```powershell
# From workspace root
azd down --purge

# Optional: Remove local environment state
Remove-Item -Recurse -Force .azure

# Create new environment
azd env new <new-env-name>
azd up
```

## Infrastructure Details

## Infrastructure Details

The `infra/main.bicep` template at the workspace root deploys:

- Azure Storage Account
- Azure AI Search Service
- Azure AI Foundry Resource (`Microsoft.CognitiveServices/accounts` kind: `AIServices`)
- Azure AI Foundry Project (`Microsoft.CognitiveServices/accounts/projects` - hubless architecture)
- Log Analytics Workspace
- Application Insights
- Model Deployments (gpt-4o-mini, text-embedding-ada-002)
- RBAC role assignments and connections

**Note:** This uses the **new Foundry project architecture** (no hub required). This is the recommended approach for building agents and working with models.

### Customizing Location

By default, the Bicep template only allows `swedencentral`. To deploy to other regions:

1. Edit `infra/main.bicep`
2. Update the `@allowed` array:

```bicep
@allowed([
  'swedencentral'
  'westeurope'
  'eastus'
  // Add your desired regions
])
```

3. Run `azd up` again

## Quick Start Summary

```powershell
# 1. Navigate to workspace root
cd d:\git-classes\pro-code-agents

# 2. Create environment and deploy
azd env new dev-swedencentral
azd up

# 3. Retrieve configuration keys
cd infra
./get-keys.sh --resource-group rg-pro-code-agents-dev-swedencentral

# 4. Use generated .env and appsettings.json in demos
cd ..
# Files are now at workspace root: .env and appsettings.json
```

## Security Notes

⚠️ **Important**: The generated `.env` and `appsettings.json` files contain sensitive credentials:

- **Location**: Both files are created at the **workspace root** (`d:\git-classes\pro-code-agents\`)
- Never commit these files to version control
- `.env` is already in `.gitignore`
- Add `appsettings.json` to `.gitignore` if not already present
- Store them securely on your local machine
- Regenerate keys if accidentally exposed

## Troubleshooting

### azd init fails to detect infrastructure

**Symptom**: Running `azd init` shows "No services were automatically detected"

**Solution**: Ensure you're running from the workspace root where `azure.yaml` and `infra/` directory exist:

```powershell
cd d:\git-classes\pro-code-agents
azd init
```

### get-keys.sh reports missing services

**Causes**:

1. Deployment hasn't completed successfully
2. Wrong resource group name
3. Insufficient permissions

**Solutions**:

```powershell
# Verify deployment status
azd env get-values
az deployment group list --resource-group <rg-name>

# Re-run deployment if needed
azd up

# Ensure you have Reader role on the resource group
az role assignment list --resource-group <rg-name> --assignee <your-user-principal-id>
```

### Location not allowed error

**Symptom**: Bicep deployment fails with location validation error

**Solution**: Update `infra/main.bicep` to include your desired region in the `@allowed` array.

### Missing .env or appsettings.json files

**Symptom**: Configuration files not found after running `get-keys.sh`

**Solution**:

- Files are created at workspace root, not in `infra/` directory
- Check: `d:\git-classes\pro-code-agents\.env` and `d:\git-classes\pro-code-agents\appsettings.json`
- Ensure `get-keys.sh` completed without errors

## Related Documentation

- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-services/what-is-ai-studio)
- [Bicep Language Reference](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
