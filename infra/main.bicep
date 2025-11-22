@allowed([
  'swedencentral'
])
@description('Azure location where resources should be deployed (e.g., swedencentral)')
param location string = 'swedencentral'

@description('Optional: Object ID (Principal ID) of the service principal to grant permissions to AI Foundry resources')
param servicePrincipalObjectId string = ''

var prefix = 'ai'
var suffix = substring(uniqueString(resourceGroup().id), 0, 3)

var storageAccountName = replace('${prefix}-storage-${suffix}', '-', '')
var logAnalyticsWorkspaceName = '${prefix}-analytics-${suffix}'
var searchServiceName = '${prefix}-search-${suffix}'
var aiFoundryName = '${prefix}-procode-${suffix}'
var aiProjectName = '${prefix}-procode-${suffix}'
var applicationInsightsName = '${prefix}-insights-${suffix}'

var cognitiveServicesUserRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'a97b65f3-24c7-4388-baec-2e87135dc908'
)
var searchServiceContributorRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
)
var aiDeveloperRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '64702f94-c441-49e6-a78b-ef80e0188fee'
)
var contributorRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'b24988ac-6180-42a0-ab88-20f7382dd24c'
)

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: {
    ProjectType: 'aoai-your-data-service'
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    dnsEndpointType: 'Standard'
    defaultToOAuthAuthentication: false
    publicNetworkAccess: 'Enabled'
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: true
    allowSharedKeyAccess: true
    largeFileSharesState: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: 'free'
  }
  properties: {
    hostingMode: 'default'
    replicaCount: 1
    partitionCount: 1
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: aiFoundryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiFoundryName
    disableLocalAuth: false
  }
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  name: aiProjectName
  parent: aiFoundry
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

resource gpt4MiniDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  name: 'gpt-4o-mini'
  parent: aiFoundry
  sku: {
    // Default quota capacity per reference subscription image
    capacity: 100
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: 'gpt-4o-mini'
      format: 'OpenAI'
    }
  }
}

// Added full GPT-4o deployment for demos referencing "gpt-4o"
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  name: 'gpt-4o'
  parent: aiFoundry
  sku: {
    // Default quota capacity (image shows 50)
    capacity: 50
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: 'gpt-4o'
      format: 'OpenAI'
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  name: 'text-embedding-ada-002'
  parent: aiFoundry
  sku: {
    // Default quota capacity (image shows 150)
    capacity: 150
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: 'text-embedding-ada-002'
      format: 'OpenAI'
    }
  }
  dependsOn: [
    gpt4MiniDeployment
    gpt4oDeployment
  ]
}

// Added model-router deployment per request
resource modelRouterDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  name: 'model-router'
  parent: aiFoundry
  sku: {
    // Default quota capacity (image shows 250)
    capacity: 250
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: 'model-router'
      format: 'OpenAI'
    }
  }
  dependsOn: [
    gpt4MiniDeployment
    gpt4oDeployment
    embeddingDeployment
  ]
}

resource projectAIFoundryRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundry.id, aiProject.id, cognitiveServicesUserRoleId)
  scope: aiFoundry
  properties: {
    roleDefinitionId: cognitiveServicesUserRoleId
    principalId: aiProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource aiFoundrySearchRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, aiFoundry.id, searchServiceContributorRoleId)
  scope: searchService
  properties: {
    roleDefinitionId: searchServiceContributorRoleId
    principalId: aiFoundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource projectSearchRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, aiProject.id, searchServiceContributorRoleId)
  scope: searchService
  properties: {
    roleDefinitionId: searchServiceContributorRoleId
    principalId: aiProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource servicePrincipalCognitiveServicesUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(servicePrincipalObjectId)) {
  name: guid(aiFoundry.id, servicePrincipalObjectId, cognitiveServicesUserRoleId)
  scope: aiFoundry
  properties: {
    roleDefinitionId: cognitiveServicesUserRoleId
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

resource servicePrincipalAIDeveloperRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(servicePrincipalObjectId)) {
  name: guid(aiFoundry.id, servicePrincipalObjectId, aiDeveloperRoleId)
  scope: aiFoundry
  properties: {
    roleDefinitionId: aiDeveloperRoleId
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

resource servicePrincipalContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(servicePrincipalObjectId)) {
  name: guid(aiFoundry.id, servicePrincipalObjectId, contributorRoleId)
  scope: aiFoundry
  properties: {
    roleDefinitionId: contributorRoleId
    principalId: servicePrincipalObjectId
    principalType: 'ServicePrincipal'
  }
}

resource searchConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  name: '${aiFoundry.name}-aisearch'
  parent: aiFoundry
  properties: {
    category: 'CognitiveSearch'
    target: 'https://${searchServiceName}.search.windows.net'
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: searchService.listAdminKeys().primaryKey
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: searchService.id
      location: location
    }
  }
}

resource storageConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  name: '${aiFoundry.name}-storage'
  parent: aiFoundry
  properties: {
    category: 'AzureBlobStorage'
    target: storageAccount.properties.primaryEndpoints.blob
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: storageAccount.listKeys().keys[0].value
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: storageAccount.id
      location: location
    }
  }
}

output storageAccountName string = storageAccountName
output logAnalyticsWorkspaceName string = logAnalyticsWorkspaceName
output searchServiceName string = searchServiceName
output aiFoundryHubName string = aiFoundryName
output aiFoundryProjectName string = aiProjectName
output applicationInsightsName string = applicationInsightsName
output searchServiceEndpoint string = 'https://${searchServiceName}.search.windows.net/'
output aiFoundryHubEndpoint string = 'https://ml.azure.com/home?wsid=${aiFoundry.id}'
output aiFoundryProjectEndpoint string = 'https://ai.azure.com/build/overview?wsid=${aiProject.id}'
