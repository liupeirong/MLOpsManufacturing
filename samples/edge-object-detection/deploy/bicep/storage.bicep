param accessTier string = 'Cool'
param environmentName string
param kind string = 'StorageV2'
param location string
param projectName string
param skuName string = 'Standard_LRS'
param skuTier string = 'Standard'

@minLength(3)
@maxLength(24)
param storageName string

resource storage_account 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  sku: {
    name: skuName
    tier: skuTier
  }
  kind: kind
  name: storageName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    accessTier: accessTier
    supportsHttpsTrafficOnly: true
  }
}

output storage_resource_id string = storage_account.id