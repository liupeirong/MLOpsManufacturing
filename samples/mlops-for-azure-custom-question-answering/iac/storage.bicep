param location string
param salt string

var storageAccountName = 'stcqamlops${uniqueString(salt)}'

resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  location: location
  name: storageAccountName
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    allowBlobPublicAccess: false
  }
}

resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-04-01' = {
  name: '${storage.name}/default/mlops'
}

var serviceSasProperties = {
    canonicalizedResource: '/blob/${storage.name}/mlops'
    signedVersion: '2021-04-01'
    signedResource: 'c'
    signedPermission: 'rw'
    signedServices: 'b'
    signedExpiry: '9999-01-01T00:00:00Z'
}

output accountName string = storage.name
output sasToken string = storage.listServiceSas('2021-04-01', serviceSasProperties).serviceSasToken
