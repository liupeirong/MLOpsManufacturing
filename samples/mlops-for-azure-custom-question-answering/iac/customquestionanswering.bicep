param location string
param salt string
@minLength(3)
@maxLength(5)
param servicePrefix string

var cqAnsweringName = 'cs-cqa-${servicePrefix}-${uniqueString(salt)}'
var cqAnsweringSearchName = 'srch-cqa-${servicePrefix}-${uniqueString(salt)}'

resource cqAnsweringSearch 'Microsoft.Search/searchServices@2020-03-13' = {
  name: cqAnsweringSearchName
  location: location
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
  }
  sku: {
    name: 'basic'
  }
}

resource cqAnswering 'Microsoft.CognitiveServices/accounts@2021-04-30' = {
  location: location
  name: cqAnsweringName
  kind: 'TextAnalytics'
  properties: {
    apiProperties: {
      qnaAzureSearchEndpointId: cqAnsweringSearch.id
      qnaAzureSearchEndpointKey: cqAnsweringSearch.listAdminKeys().primaryKey
    }
    customSubDomainName: cqAnsweringName
    publicNetworkAccess: 'Enabled'
  }
  sku: {
    name: 'S'
  }
}

output endpoint string = cqAnswering.properties.endpoint
output key string = cqAnswering.listKeys().key1
