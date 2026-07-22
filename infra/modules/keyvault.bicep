param name string
param location string

resource kv 'Microsoft.KeyVault/vaults@2026-02-01' = {
  name: name
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enabledForTemplateDeployment: true
  }
}

output uri string = kv.properties.vaultUri
output id string = kv.id
