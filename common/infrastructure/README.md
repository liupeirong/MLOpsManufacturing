[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/provision-azure-infra?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=27&branchName=main)

# Overview

The samples in this repo run on Azure ML. Even when you can run parts of them locally, they log metrics to Azure ML. So the first thing to do is to provision Azure resources.

1. In Azure DevOps create a variable group called `iac-aml-vg` with the following variables:

| name | description |
| --- | ----------- |
| AZURE_RM_SVC_CONNECTION | Azure DevOps service connection to Azure subscription or resource group |
| BASE_NAME | a unique name used as prefix for Azure resources to be provisioned |
| LOCATION | Azure region where the resources should be provisoned |
| RESOURCE_GROUP | Azure resource group name in which the resources should be provisioned |
| WORKSPACE_NAME | Azure ML workspace name |

> Note: The credential used for AZURE_RM_SVC_CONNECTION must have minimum `contributor` role to the RESOURCE_GROUP.

2. Create an Azure DevOps pipeline from [iac-create-environment-pipeline-arm.yml](common/infrastructure/iac-create-environment-pipeline-arm.yml), and run the pipeline to provision the resources.

3. Optionally create another pipeline from [iac-remove-environment-pipeline.yml](common/infrastructure/iac-create-environment-pipeline.yml) that can be used to remove the resource group specified in the RESOURCE_GROUP variable.
