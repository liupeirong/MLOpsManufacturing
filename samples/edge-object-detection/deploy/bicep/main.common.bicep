param location string
param projectName string
param environmentName string
param keyVaultName string
param servicePrincipalObjectId string
param containerRegistryName string
param appInsightsName string

var defaultAccessPolicies = [
  {
    tenantId: subscription().tenantId
    objectId: servicePrincipalObjectId
    permissions: {
      keys: [
        'get'
        'list'
        'update'
        'create'
        'import'
        'delete'
        'recover'
        'backup'
        'restore'
      ]
      secrets: [
        'get'
        'list'
        'set'
        'delete'
        'recover'
        'backup'
        'restore'
      ]
      certificates: [
        'get'
        'list'
        'update'
        'create'
        'import'
        'delete'
        'recover'
        'backup'
        'restore'
        'managecontacts'
        'manageissuers'
        'getissuers'
        'listissuers'
        'setissuers'
        'deleteissuers'
      ]
    }
  }
]
var defaultTags = {
  keyVaultExists: false
}
// If the resource group is deployed through a CLI, it must have existing tags otherwise resourceGroup.tags is not available to use
// If the resource group is deployed through the portal, this is not an issue
// Github issue: https://github.com/Azure/bicep/issues/2101
var existingTags = resourceGroup().tags != null ? resourceGroup().tags : {}
var keyVaultExists = bool(union(defaultTags, existingTags)['keyVaultExists'])
var accessPolicies = keyVaultExists ? reference(resourceId('Microsoft.KeyVault/vaults', keyVaultName), '2019-09-01').accessPolicies : defaultAccessPolicies

module ai './appinsights.bicep' = {
  name: 'appinsightsDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    appInsightsName: appInsightsName
  }
}

module acr './containerregistry.bicep' = {
  name: 'acrDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    containerRegistryName: containerRegistryName
  }
}

module kv './keyvault.bicep' = {
  name: 'kvDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    keyVaultName: keyVaultName
    accessPolicies: accessPolicies
    existingTags: existingTags
  }
}
