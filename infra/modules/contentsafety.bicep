param name string
param location string
param skuName string = 'F0'

resource safety 'Microsoft.CognitiveServices/accounts@2026-05-01' = {
  name: name
  location: location
  kind: 'ContentSafety'
  sku: { name: skuName }
  properties: {
    customSubDomainName: name
  }
}

output endpoint string = safety.properties.endpoint
output id string = safety.id
