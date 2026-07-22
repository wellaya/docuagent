param name string
param location string
param skuName string = 'free'

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: name
  location: location
  sku: { name: skuName }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
  }
}

output endpoint string = 'https://${name}.search.windows.net'
output id string = search.id
