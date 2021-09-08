targetScope = 'subscription'

param location string
param name string

resource resourceGroups 'Microsoft.Resources/resourceGroups@2020-10-01' = {
  name: name
  location: location
}
