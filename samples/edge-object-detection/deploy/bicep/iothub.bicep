param location string
param iotHubName string
param skuName string = 'S1'
param skuUnits int = 1
param environmentName string
param projectName string
param hubEndpointtRetentionTime int = 1
param hubEndpointPartitionCount int = 4
param feature string = 'None'

resource iothub 'Microsoft.Devices/IotHubs@2020-03-01' = {
  name: iotHubName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  sku: {
    name: skuName
    capacity: skuUnits
  }
  properties: {
    eventHubEndpoints: {
      events: {
        retentionTimeInDays: hubEndpointtRetentionTime
        partitionCount: hubEndpointPartitionCount
      }
    }
    routing: {
      fallbackRoute: {
        name: '$fallback'
        source: 'DeviceMessages'
        condition: 'true'
        endpointNames: [
          'events'
        ]
        isEnabled: true
      }
    }
    messagingEndpoints: {
      fileNotifications: {
        lockDurationAsIso8601: 'PT1M'
        ttlAsIso8601: 'PT1H'
        maxDeliveryCount: 10
      }
    }
    enableFileUploadNotifications: false
    cloudToDevice: {
      maxDeliveryCount: 10
      defaultTtlAsIso8601: 'PT1H'
      feedback: {
        lockDurationAsIso8601: 'PT1M'
        ttlAsIso8601: 'PT1H'
        maxDeliveryCount: 10
      }
    }
    features: feature
  }
}
