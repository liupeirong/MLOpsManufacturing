targetScope = 'subscription'

@description('Name of the resource group')
param resourceGroupName string = 'custom-question-answering-rg'
@description('Azure region for all services')
param location string = 'westeurope'
@description('Salt to generate globally unique names')
param salt string = 'koreacentral'

module resourceGroups './resourceGroup.bicep' = {
  name: resourceGroupName
  params: {
    location: location
    name: resourceGroupName
  }
}

module cqa1 './customquestionanswering.bicep' = {
  name: 'customQuestionAnswering1'
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    salt: salt
    servicePrefix: '001'
  }
  dependsOn: [
    resourceGroups
  ]
}

module cqa2 './customquestionanswering.bicep' = {
  name: 'customQuestionAnswering2'
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    salt: salt
    servicePrefix: '002'
  }
  dependsOn: [
    resourceGroups
  ]
}


output cqa1_endpoint string = cqa1.outputs.endpoint
output cqa1_key string = cqa1.outputs.key
output cqa2_endpoint string = cqa2.outputs.endpoint
output cqa2_key string = cqa2.outputs.key
