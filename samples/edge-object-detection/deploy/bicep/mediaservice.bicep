param mediaServicesName string
param location string
param environmentName string
param projectName string
param storageId string

resource media_service 'Microsoft.Media/mediaServices@2020-05-01' = {
  name: mediaServicesName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    storageAccounts: [
      {
        id: storageId
        type: 'Primary'
      }
    ]
  }
}
