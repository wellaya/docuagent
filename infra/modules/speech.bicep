param name string
param location string
param skuName string = 'F0'

resource speech 'Microsoft.CognitiveServices/accounts@2026-05-01' = {
  name: name
  location: location
  kind: 'SpeechServices'
  sku: { name: skuName }
  properties: {
    customSubDomainName: name
  }
}

output endpoint string = speech.properties.endpoint
output id string = speech.id
