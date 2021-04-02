param appInsightsName string
param appType string = 'web'
param environmentName string
param kind string = 'web'
param location string
param projectName string

resource app_insights 'Microsoft.Insights/components@2020-02-02-preview' = {
  location: location
  name: appInsightsName
  kind: kind
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    Application_Type: appType
  }
}
