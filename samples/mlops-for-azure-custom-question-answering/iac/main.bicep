targetScope = 'subscription'

@description('Name of the resource group')
param resourceGroupName string = 'custom-question-answering-rg'
@description('Azure region for all services')
param location string = 'northeurope'
@description('Salt to generate globally unique names')
param salt string = 'saltissalty'
@description('Custom Question Answering API version path')
param apiversion string = 'qnamaker/5.0-preview2'

module resourceGroups './resourceGroup.bicep' = {
  name: resourceGroupName
  params: {
    location: location
    name: resourceGroupName
  }
}

module cqa1 './customquestionanswering.bicep' = {
  name: 'customQuestionAnsweringEdit'
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    salt: salt
    servicePrefix: 'edit'
  }
  dependsOn: [
    resourceGroups
  ]
}

module cqa2 './customquestionanswering.bicep' = {
  name: 'customQuestionAnsweringProd'
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    salt: salt
    servicePrefix: 'prod'
  }
  dependsOn: [
    resourceGroups
  ]
}

module str 'storage.bicep' = {
  name: 'storageAccount'
  scope: resourceGroup(resourceGroupName)
  params: {
    location: location
    salt: salt
  }
  dependsOn: [
    resourceGroups
  ]
}


output cqa1_endpoint string = '${cqa1.outputs.endpoint}${apiversion}'
output cqa1_key string = cqa1.outputs.key
output cqa2_endpoint string = '${cqa2.outputs.endpoint}${apiversion}'
output cqa2_key string = cqa2.outputs.key
output storage_account string = str.outputs.accountName
output storage_sas string = str.outputs.sasToken
