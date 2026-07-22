@description('Location for all resources')
param location string = resourceGroup().location

@description('Base name used to derive resource names')
param baseName string = 'docuagent'

@description('Deploy Azure OpenAI / Foundry model resources. Set false if quota not yet approved.')
param deployOpenAI bool = true

var uniqueSuffix = uniqueString(resourceGroup().id)
var searchName = '${baseName}-search-${uniqueSuffix}'
var docIntelName = '${baseName}-docintel-${uniqueSuffix}'
var speechName = '${baseName}-speech-${uniqueSuffix}'
var contentSafetyName = '${baseName}-safety-${uniqueSuffix}'
var kvName = '${baseName}kv${uniqueSuffix}'
var foundryName = '${baseName}-foundry-${uniqueSuffix}'
var appInsightsName = '${baseName}-appi-${uniqueSuffix}'
var logAnalyticsName = '${baseName}-log-${uniqueSuffix}'

module logAnalytics 'modules/loganalytics.bicep' = {
  name: 'logAnalyticsDeploy'
  params: {
    name: logAnalyticsName
    location: location
  }
}

module appInsights 'modules/appinsights.bicep' = {
  name: 'appInsightsDeploy'
  params: {
    name: appInsightsName
    location: location
    workspaceId: logAnalytics.outputs.id
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyVaultDeploy'
  params: {
    name: kvName
    location: location
  }
}

module search 'modules/search.bicep' = {
  name: 'searchDeploy'
  params: {
    name: searchName
    location: location
    skuName: 'free'
  }
}

module docIntel 'modules/docintel.bicep' = {
  name: 'docIntelDeploy'
  params: {
    name: docIntelName
    location: location
    skuName: 'F0'
  }
}

module speech 'modules/speech.bicep' = {
  name: 'speechDeploy'
  params: {
    name: speechName
    location: location
    skuName: 'F0'
  }
}

module contentSafety 'modules/contentsafety.bicep' = {
  name: 'contentSafetyDeploy'
  params: {
    name: contentSafetyName
    location: location
    skuName: 'F0'
  }
}

module foundry 'modules/foundry.bicep' = if (deployOpenAI) {
  name: 'foundryDeploy'
  params: {
    name: foundryName
    location: location
  }
}

output searchEndpoint string = search.outputs.endpoint
output docIntelEndpoint string = docIntel.outputs.endpoint
output speechEndpoint string = speech.outputs.endpoint
output contentSafetyEndpoint string = contentSafety.outputs.endpoint
output keyVaultUri string = keyVault.outputs.uri
output appInsightsConnectionString string = appInsights.outputs.connectionString
