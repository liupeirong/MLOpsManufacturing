param containerRegistryName string
param environmentName string
param location string
param projectName string
param skuName string = 'Basic'

resource acr 'Microsoft.ContainerRegistry/registries@2019-05-01' = {
  sku: {
    name: skuName
  }
  name: containerRegistryName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    adminUserEnabled: true
  }
}
