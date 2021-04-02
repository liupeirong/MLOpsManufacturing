param location string
param projectName string
param environmentName string
param iotHubName string
param mediaServicesName string
param logAnalyticsName string

@minLength(3)
@maxLength(24)
param storageName string

module storage './storage.bicep' = {
  name: 'storageDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    storageName: storageName
  }
}

module ms './mediaservice.bicep' = {
  name: 'mediasserviceDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    mediaServicesName: mediaServicesName
    storageId: storage.outputs.storage_resource_id
  }
}

module iot './iothub.bicep' = {
  name: 'iotDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    iotHubName: iotHubName
  }
}

module la './loganalytics.bicep' = {
  name: 'loganalyticsDeploy'
  params: {
    location: location
    projectName: projectName
    environmentName: environmentName
    logAnalyticsName: logAnalyticsName
  }
}