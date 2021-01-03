# Overview

This repo contains samples of machine learning (ML) projects we have often seen in the manufacturing industry. For example, using image classification or object detection for quality control and safety monitoring. The code here isn't specific to manufacturing, rather we are just using these samples to showcase how to build, deploy, and operationalize ML projects in production with good engineering practices such as unit testing, CI/CD, model experimentation tracking, and observability in model training and inferencing.

Samples in this project leverage the basic ideas used in [MLOpsPython](https://github.com/microsoft/MLOpsPython). While MLOpsPython lays the foundation for operationalizing ML, we aim to provide representative samples and docs to 
- provide a sounding startpoint to build a production quality ML solution of certain frameworks such as Tensorflow or Yolo.
- demonstrate approaches and techniques for cross-cutting concerns such as unit testing and logging.
- document how to solve some of the challenges encountered in building ML solutions, such as security, data management, local vs. cloud based development and more. 

## Repo Structure

This repo contains sample code and definition of Azure DevOps pipelines for CI/CD. These pipelines run in [this Azure DevOps project](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build?view=folders). ML pipelines run in the Azure environment deployed using the Azure DevOps pipelines.

The folders are structured as following - 
```
- common # contains code common across samples
    - infrastructure # code to provision Azure resources to run the samples
- docs # how-tos and best practices
- samples # each sample may have different folders, below is a typical example
    - <sample 1>
        - .devcontainer # VSCode dev container you can optionally use for development
        - devops_pipelines # Azure DevOps CI/CD pipeline definition
        - local_development # scripts for creating a local dev environment without having to have a VSCode dev container
        - ml_model # code for building the ML model
        - ml_service # code for building ML pipelines
        - README.md # explains what the sample is demonstrating and how to run it
    - <sample 2>
    - ...
```

## Samples

- [Image classification with Tensorflow and Keras](samples/image-classification-tensorflow) demonstrates how to use Azure DevOps and Azure ML to build, train, evaluate, and track models, including how to retrain on new data. 
- [Run non-Python code as a step in ML Pipeline](samples/non-python-preprocess) demonstrates how to run non Python custom code as a step in Azure ML pipelines. We've seen many cases where companies already have custom code they use to preprocess data before training a ML model. This sample also demonstrates how to use PyTest to mock Azure ML SDK for unit testing.

## How to Get Started

1. Clone the repo.
2. If you are only interested in one sample,
    * if your dev machine is capable of running [VSCode dev container](https://code.visualstudio.com/docs/remote/containers-tutorial), you can open the folder of the sample in VSCode, and reopen in a container as VSCode prompts you. Once VSCode builds the container, you can do all the development inside that container from that point on.
    * if you don't want to develop in a container, you can go to the samples's `local_development` folder and run a script to create a conda environment for development. Refer to each sample's README for details.
3. You can also open the entire project in VSCode. Refer to the README of the sample you are interested in, create a conda environment, and pick the Python interpreter from the environment in VSCode.
4. Set up an Azure DevOps project to connect to your source repository. Configure the pipelines using their yaml definitions in this repo:
    * start with [common/infrastructure](common/infrastructure/README.md) to create an Azure environment to run the samples.
    * follow README of the sample of interest to create the Azure DevOps pipelines. The pipelines are configured for continuous integration by default, so they automatically kick off for pull request validations and merging into the main branch.

## Contributing

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
