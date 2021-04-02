param location string
param environmentName string
param projectName string
param virtualNetworkName string
param vNetIpPrefix string = '10.0.0.0/16'

resource virtual_network 'Microsoft.Network/virtualNetworks@2020-06-01' = {
  name: virtualNetworkName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    addressSpace: {
      addressPrefixes: [
        vNetIpPrefix
      ]
    }
  }
}

output vnetName string = virtual_network.name
