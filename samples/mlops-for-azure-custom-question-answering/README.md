# Overview

Demonstrates how to use Azure DevOps to test and publish Custom Question Answering (formerly QnA Maker) Knowlegebases
from a editing stage/environment to a production stage/environment.

__What does this sample demonstrate__:

* Integrate Accuracy Test for Knowledgebases into Azure Pipelines
* Record Knowledgbase data, test data set and test result with Azure Storage
* Collect Active Learning Feedback data from production and display it in the editing Knowledgebase

__What doesn't this sample demonstrate__:

* How to increase accuracy of a Knowledgebase

## Model Tracking and Dataset Management

In case of Custom Question Answering the Knowledgebase data resembles the model. We track the dataset/model within
Azure Pipelines as a `Pipeline Artifact` and upload it to a storage account. Where it can be downloaded and redeployed.

## Dependency Management

This sample uses Azure Pipelines, Python scripts to interact with the Custom Question Answering API and an Accuracy Test tool
written in TypeScript.

* For the TypeScript part `npm` is used and the dependencies are managed in [package.json](accuarcy_test/package.json).
* For the Python part `pip` is used and the dependencies are managed in [pip-requirements.txt](kb/pip-requirements.txt).

> We recommend to use the devcontainer provided which has all tools preinstalled. Select `Remote Containers: Open Folder in Container...` from the VSCode command palette and navigate to this samples subfolder `samples/mlops-for-azure-custom-question-answering/`

# Getting Started

## Prerequisite

1. Docker & VSCode with Remote-Containers extension [installed](https://code.visualstudio.com/docs/remote/containers#_getting-started)
1. Fork of this repo on your [GitHub Account](https://github.com/join)
1. Create a [GitHub PAT]((https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)) with scope `admin:repo_hook`
1. Azure DevOps Organization with an [empty new project](https://docs.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops&tabs=preview-page)

## Create the Azure resources

## Configure Azure DevOps Pipelines

## Run the Pipelines

## Cleanup
