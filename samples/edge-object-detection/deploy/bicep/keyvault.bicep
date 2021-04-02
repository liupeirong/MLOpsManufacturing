param location string
param projectName string
param environmentName string
param keyVaultName string
param accessPolicies array
param existingTags object
param createMode string = 'default'
param skuFamily string = 'A'
param skuName string = 'standard'
param tenantId string = subscription().tenantId


var updatedTags = {
  keyVaultExists: true
}

resource keyvault 'Microsoft.KeyVault/vaults@2019-09-01' = {
  name: keyVaultName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    sku: {
      family: skuFamily
      name: skuName
    }
    tenantId: tenantId
    createMode: createMode
    enabledForTemplateDeployment: true
    accessPolicies: accessPolicies
  }
}

resource tags 'Microsoft.Resources/tags@2020-10-01' = {
  name: 'default'
  properties: {
    tags: union(existingTags, updatedTags)
  }
  dependsOn: [
    keyvault
  ]
}
