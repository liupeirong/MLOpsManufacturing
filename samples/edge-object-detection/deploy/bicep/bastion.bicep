param location string
param environmentName string
param projectName string
param bastionHostName string
param virtualNetworkName string
param bastionSubnetIpPrefix string = '10.0.0.0/27'

var publicIpName = 'pip-${bastionHostName}'
var subnetName = '${virtualNetworkName}/AzureBastionSubnet'

resource public_ip 'Microsoft.Network/publicIPAddresses@2020-06-01' = {
  name: publicIpName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2020-06-01' = {
  name: subnetName
  properties: {
    addressPrefix: bastionSubnetIpPrefix
  }
}

resource bastion_host 'Microsoft.Network/bastionHosts@2020-06-01' = {
  name: bastionHostName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    ipConfigurations: [
      {
        name: 'IpConf'
        properties: {
          subnet: {
            id: subnet.id
          }
          publicIPAddress: {
            id: public_ip.id
          }
        }
      }
    ]
  }
}
