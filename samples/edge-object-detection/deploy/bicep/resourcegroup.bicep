param environmentName string
param projectName string
param location string
param resourceGroupName string

targetScope = 'subscription'

resource rg 'Microsoft.Resources/resourceGroups@2020-10-01' = {
  location: location
  name: resourceGroupName
  tags: {
    Environment: environmentName
    Project: projectName
  }
}
