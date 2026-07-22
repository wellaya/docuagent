param name string
param location string
param skuName string = 'F0'

resource docIntel 'Microsoft.CognitiveServices/accounts@2026-05-01' = {
  name: name
  location: location
  kind: 'FormRecognizer'
  sku: { name: skuName }
  properties: {
    publicNetworkAccess: 'Enabled'
    customSubDomainName: name
  }
}

output endpoint string = docIntel.properties.endpoint
output id string = docIntel.id
