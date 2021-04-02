param environmentName string
param location string
param projectName string
param logAnalyticsName string

@allowed([
  'Standalone'
  'PerNode'
  'PerGB2018'
])
@description('Specifies the service tier of the workspace: Standalone, PerNode, Per-GB')
param sku string = 'PerGB2018'

// Deploy Log Analytics Workspace
resource la_workspace 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: logAnalyticsName
  location: location
  tags: {
    Environment: environmentName
    Project: projectName
  }
  properties: {
    sku: {
      name: sku
    }
  }
}

// Deploy Container Insights to Log Analytics Workspace
resource container_insights 'Microsoft.OperationsManagement/solutions@2015-11-01-preview' = {
  location: location
  name: 'ContainerInsights(${logAnalyticsName})'
  properties: {
    workspaceResourceId: la_workspace.id
  }
  plan: {
    name: 'ContainerInsights(${logAnalyticsName})'
    promotionCode: ''
    product: 'OMSGallery/ContainerInsights'
    publisher: 'Microsoft'
  }
}
