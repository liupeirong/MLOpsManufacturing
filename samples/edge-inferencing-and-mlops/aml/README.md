# Simple Azure ML Pipeline <!-- omit in toc -->

This project contains the code required to run training and validation on Azure ML.
It also contains code for setting up a data drift monitor in Azure ML.

These python files leverage the files in the `model` directory to train and save the model in AML.
There is also a script to build the dataset in AML if it does not exists (don't add this script to a CI/CD pipeline).

## Sections <!-- omit in toc -->

- [Getting started](#getting-started)
- [AML files](#aml-files)
  - [create_dataset.py](#create_datasetpy)
  - [train_model.py](#train_modelpy)
- [Data Drift](#data-drift)
- [Simple Model](#simple-model)
- [References](#references)

## Getting started

The following describes how to run the scripts in the AML folder.

1. Install VS Code (you can also use an Azure ML compute instance). You can also use a virtual environment.

1. Within terminal, navigate to the `aml` folder.

1. Install requirements with `pip install -r requirements.txt`.

1. Create a `.env` file with the following values. The example below reflects the connection to a sample resource group.

    ```dotenv
    SUBSCRIPTION_ID="{Subscription-id}"
    WORKSPACE_RESOURCE_GROUP="{wrkspace-rg}"
    DATASTORE_RESOURCE_GROUP="{wrkspace-rg}"

    AAD_TENANT_ID="{Tenant-ID}"
    AAD_SERVICE_PRINCIPAL_ID="{SP-ID}"
    AAD_SERVICE_PRINCIPAL_SECRET="{SP-secret}"

    WORKSPACE_NAME="{AML-workspace-name}"
    COMPUTE_TARGET_NAME="{AML-compute-target-name}"
    # This is the default workspace name
    DATASTORE_NAME="workspaceblobstore"
    DATASTORE_CONTAINER_NAME="{datastore-container-name}"

    ENVIRONMENT_NAME=AzureML-sklearn-0.24-ubuntu18.04-py37-cuda11-gpu
    ENVIRONMENT_VERSION=1
    ENVIRONMENT_BASE_IMAGE=mcr.microsoft.com/azureml/sklearn-0.24.1-ubuntu18.04-py37-cpu-inference:latest

    DATA_STORAGE_ACCOUNT_NAME="{blob-storage-account-name}"
    DATA_STORAGE_ACCOUNT_KEY="{blob-storage-account-key}"
    ```

1. To create a test dataset, simply run `python -m create_dataset`.

1. To train a model, simply run `python -m train_model`.

## AML files

There are multiple python scripts associated with the model training. Below are descriptions of the actions executed within each step.

### create_dataset.py

This script creates the dataset in AML using the `create_dataset.py` script in the `model` directory.

### train_model.py

This script trains the model in AML and registers the model using `main.py` and `register_model.py` from the `model` directory.

## Data Drift

To learn more about data drift monitor in AML, what it does and how to run it, check out [how to run data drift](./../docs/ml-data-drift.md).

## Simple Model

To learn more about how to run the model, check out [how to train and register a model](./../model/README.md).

>Note: The AML folder needs the model folder to run, but not vice versa.

## References

- [What are Azure Machine Learning pipelines?](https://docs.microsoft.com/azure/machine-learning/concept-ml-pipelines)
