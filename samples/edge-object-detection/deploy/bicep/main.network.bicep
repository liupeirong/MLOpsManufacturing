param location string
param projectName string
param environmentName string
param virtualNetworkName string
param bastionHostName string

module network './network.bicep' = {
  name: 'networkDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    virtualNetworkName: virtualNetworkName
  }
}

module bastion './bastion.bicep' = {
  name: 'bastionDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    bastionHostName: bastionHostName
    virtualNetworkName: network.outputs.vnetName
  }
}
