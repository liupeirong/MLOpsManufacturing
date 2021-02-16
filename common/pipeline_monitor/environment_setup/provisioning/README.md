# Overview

This folder contains scripts to create Azure resources for sample 'pipeline_monitor'.

## Getting Started

1. This code needs to get Azure ML context for remote or offline runs. Create Azure resources as documented [here](https://github.com/liupeirong/MLOpsManufacturing/tree/main/common/infrastructure).

2. Create an Azure DevOps pipeline from [iac-create-environment-functions-arm.yml](iac-create-environment-functions-arm.yml), and run the pipeline to provision the resources.