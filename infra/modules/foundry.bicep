param name string
param location string
param modelName string = 'gpt-4o-mini'
param modelVersion string = '2024-07-18'
param modelCapacity int = 10

resource foundry 'Microsoft.CognitiveServices/accounts@2026-05-01' = {
  name: name
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
  }
}

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2026-05-01' = {
  parent: foundry
  name: modelName
  sku: {
    name: 'Standard'
    capacity: modelCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

output endpoint string = foundry.properties.endpoint
output id string = foundry.id
