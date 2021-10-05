# MLOps and Edge Inferencing Solution <!-- omit in toc -->

This repo has code and pipelines that enable full end to end deployment of
training a model using Azure Machine Learning (AML), and packaging that model into
a container that can run on the edge for efficient inferencing.

This is useful for many different scenarios where you would want to run ML
on the edge, say in a factory setting for tooling recommendations or image recognition.

This repo walks through different portions of that solution
and explains how to set them up if you have a similar scenario.

## Sections <!-- omit in toc -->

- [Folder Structure](#folder-structure)
- [Azure Resources Needed](#azure-resources-needed)
- [Inferencing Service](#inferencing-service)
  - [How to Swap In Your Own Model](#how-to-swap-in-your-own-model)
- [Model Training](#model-training)
- [AML](#aml)

## Folder Structure

The root of this repository has a few different directories with the following purposes:

- `.pipelines/`

    This folder is where we store pipeline files for (PR) build validation, CI, and CD for this project.
    This repo comes fully with pipelines to deploy these files to your own Azure DevOps instance
    and get your project up and running right away (with just a couple variable changes).

- `aml/`

    This folder contains the scripts needed to train the model in Azure Machine Learning (AML).
    The scripts both train and publish the model.
    There is another script used to create the dataset, but this script is intended to run once.

    This folder also has information and a sample script
    for how to use and deploy the Data Drift Monitor feature in AML.
    ``

- `docs/`

    This folder contains documents for different parts of the project.
    The [README](docs/README.md) has information about what docs are there.

- `grpc_inferencing_service/`

    This folder contains the code for an inferencing service that can run on the edge.
    It also includes information on how to package it, integration test it, and run it.

- `model/`

    This folder contains information and sample python files for building the dataset,
    building the model, and saving the model.

- `protos/`

    This folder contains the [proto files](https://grpc.io/docs/what-is-grpc/introduction/)
    that define the contract for input and output to the inferencing service.

    The reason that these live at the root of the repo instead of with the inferencing service
    is because other platform components that live elsewhere in the repo might need to know
    the contracts for communicating with the inferencing service.

- `scripts/`

    This folder contains miscellaneous scripts used throughout the repo
    and that can be re-used in other repos.

There are also a handful of files at the root of the repo,
primarily for linting that gets done with all build validations
to make sure the repo stays clean and the code stays [mostly :-)] bug free.

## Azure Resources Needed

This repo does not include infrastructure as code (IaC) to set up all the azure resources needed,
however the ones that are needed can use the standard out of the box options.

The resources needed to be deployed to an Azure Resource Group for this project are:

- Azure Machine Learning (AML): [How to create](https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources)
- Azure Container Registry (ACR): [How to create](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal)

## Inferencing Service

This folder contains the code, integration testing, and dockerfile's
for a gRPC based inferencing service that can run on the edge.

gRPC is useful because it sends smaller packets of information with less overhead,
so it can be highly useful in edge scenarios with low connectivity or scenarios where very low latency is needed.

If you want to utilize just this portion of the project it can be taken as a standalone portion of the repo.
All you need is the `protos/` and `grpc_inferencing_service/` directories.
I would also recommend taking a few pipeline files relating to the inferencing service
to set up build and deploy pipelines in your Azure DevOps.

For more in depth information on the inferencing service, see the [README](grpc_inferencing_service/README.md)
in the `grpc_inferencing_service/` folder

### How to Swap In Your Own Model

If you want to leverage the code for the inferencing service to get
your own edge container up and running but with a different model
there are 3 areas where you will need to make changes.

1. The [inference.proto file](protos/inference.proto)

   This file defines the inputs that you need to send into your model to get an inference.
   For this simple example we have done `x1` and `x2` but you can change this to whatever you want.
   For example you could have a model that takes in `string name`, `int height`, and `datetime time_of_day`
   and returns `double tiredness`.
   You make all those changes in the [inference.proto](protos/inference.proto) and you are good to go.

1. The RequestData class in the [inference_service.py file](grpc_inferencing_service/service/core/inference_service.py)

   Inside the `inference_service.py` file there is a class named RequestData.
   The purpose of this class is to map the proto input to a python class for added clarity
   about what properties a model needs, and increased code readability and maintainability.

   This class can be used for input validation, or adding in any information
   that could be constant and thus not passed in on every request,
   or making any computations on the request data before sending it to the model.
   Basically it takes in the contract from the proto,
   and extends it to have more functionality and be more developer friendly.

   Because this is mapping the proto, if the proto file changes, this class should change as well.

1. The model file stored in `grpc_inferencing_service/service/lib/classifier.pkl`

   Put whatever trained model you want here.
   It needs to be named exactly that, but if you want to expand into multiple model files
   you can see where `classifier.pkl` is referenced and use that as a starting point for changing the code.

## Model Training

For information on training your own model that can be used with this inferencing service
see the documentation in the model folder [here](model/README.md).

## AML

This folder contains the scripts needed to train the model in Azure Machine Learning (AML).

There is a script to create a test dataset and a script to train and publish the model.
These sample scripts are a great example of how to train and register a model.

The script uses the model python code from [the `model` folder](./model) and runs the [`main.py`](./model/main.py)
to train the model, and the [`register_model.py`](./model/register_model.py) to actually register it in Azure ML.

For more information on how to run the code in this folder, [click here](./aml/README.md).
