[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/provision-azure-infra?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=27&branchName=main)

# Overview

The samples in this repo run on Azure ML. Even when you run parts of them locally, they need to retrieve an offline context from Azure ML. So the first thing to do is to provision Azure resources.

1. In Azure DevOps create a variable group called `iac-aml-vg` with the following variables:

| name | description |
| --- | ----------- |
| AZURE_RM_SVC_CONNECTION | Azure DevOps service connection to Azure Subscription or Resource Group |
| BASE_NAME | a unique name used as prefix for Azure resources to be provisioned |
| LOCATION | Azure region where the resources should be provisioned |
| RESOURCE_GROUP | Azure Resource Group name in which the resources should be provisioned |
| SUBSCRIPTION_ID | Azure Subscription ID |
| WORKSPACE_NAME | Azure ML Workspace name |

> Note: The credential used for AZURE_RM_SVC_CONNECTION must have minimum `contributor` role to the RESOURCE_GROUP.

2. Create an Azure DevOps pipeline from [iac-create-environment-pipeline-arm.yml](iac-create-environment-pipeline-arm.yml), and run the pipeline to provision the resources.

> Note:`(BASE_NAME)-AML-KV` is used by Azure ML, and `kv-common-(BASE_NAME)` will be used by user to store their own secrets.

3. Optionally create another pipeline from [iac-remove-environment-pipeline.yml](iac-remove-environment-pipeline.yml) that can be used to remove the entire Resource Group where resources were previously provisioned.
