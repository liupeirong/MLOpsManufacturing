# Problem Statement
There are many variables used in any Azure Machine Learning (AML) projects, including variables for Azure resources, Azure DevOps (ADO) pipelines, AML experiments and more. There are also many different ways to store them, for example, in environment variables, ADO variable templates, ADO variable groups, or supply them directly in command line. What's the best practice to manage these variables - which variables should be store where?

# What are the different types of variables?

Broadly speaking, an ML project has the following categories of variables.

## Infrastructure variables
Infrastructure variables define _where_ the solution runs. In Azure, this will be Azure resources such as:
* Azure Subscription
* Resource Group
* Azure Storage Account
* Azure Container Registry
* Azure ML workspace

For Azure DevOps to deploy or access Azure resources, we also need to create Azure DevOps `Service Connections` and define variables that represent these Service Connections to be used in Azure DevOps pipelines.

## Application variables
Application variables define _how_ the solutions runs. They don't necessarily change from environment to environment, but are flexible as variables rather than hardcoded in source code. For example:
* compute machine spec for ML model training
* AML Data Store name, Dataset name, and the path of the training data
* the URLs of the images used for smoke testing

## Machine Learning variables
Machine Learning variables define _how_ the data should be processed and trained. For example, 
* the size to which the images should be normalized to
* the number of epochs for ML training
* hyperparameters for ML training

# Where to store the variables?

Where to store the variables depends on how the variables change. For example, 
* if you store them in a file that's checked into the source repo, then they can't change unless you check in a new version or create another file.
* if you store them in Azure DevOps variable groups, then you can create multiple variable groups for multiple DevOps pipelines for different environments, such as dev, test, staging, and production. However, for variables that don't need to change from environment to environment, you don't want to specify them over and over in all variable groups.
* if you want to experiment model training with different parameters, then you need to be able to specify these parameters as you trigger the ML pipelines.

> Please note the difference between *Azure DevOps pipelines* and *Azure ML pipelines*. Azure DevOps pipelines are defined as yaml and triggered upon code change. They are responsible for building, testing, and deploying code, including publishing Azure ML pipelines. Azure ML pipelines are used for preprocessing data, or training, evaluating, and registering ML models. They are defined in Python code and can be triggered to run from Azure DevOps pipelines, or manually or programmatically when new data arrives outside of Azure DevOps.

Here are some suggestions on where to store different types of variables:
* Store infrastructure variables in Azure DevOps variable groups, and reference them in Azure DevOps pipelines. When you need to run the solution in a new environment, replicate the variable groups and set the variables to the new environment, then replicate the pipelines to use the new variable groups for the new environment.
* For application variables that don't necessarily change from environment to environment, define their default values in Azure DevOps variable templates so that they don't need to be specified in variable groups. Reference them in DevOps pipelines such that if specified in variable groups, their values overwrite the defaults in variable templates. 
* Create ML variables for AML pipelines so that data scientists can run them for experimentation without dependency on Azure DevOps. You can define the default values for ML varaibles in a file and have the ML code read the file if no ML pipeline parameters are present. This way when Azure DevOps triggers ML pipelines, sensible defaults are used, and Azure DevOps can focus on ensuring the code runs rather than training an accurate model.
* When developing on the local machine, store infrastructure and application variables in `.env`.
* Avoid secret variables as much as possible by using Azure built-in constructs such as Managed Identity. If you must have secrets, store them in Azure Key Vault.

For example, this is how variables are managed in this project:
* common infrastructure variables required to run the samples are stored in Azure DevOps variable groups defined [here](../common/infrastructure/README.md). They are referenced in the [infrastructure deployment pipeline](../common/infrastructure/iac-create-environment-pipeline-arm.yml#L27). 
* additional infrastructure variables for the image-classification-tensorflow sample are defined [here](../samples/image-classification-tensorflow#cicd-in-azure-devops). They are referenced in, for example, the [train-evaluate-register DevOps pipeline](../samples/image-classification-tensorflow/devops_pipelines/03-train-evaluate-register-model.yml#L48) 
* application variables such as the training cluster machine spec have their defaults defined in [devops_pipelines/variable-template.yml](../samples/image-classification-tensorflow/devops_pipelines/variables-template.yml) so you don't have to specify all of them in variable groups, however, based on [the order they are defined in the pipeline](../samples/image-classification-tensorflow/devops_pipelines/03-train-evaluate-register-model.yml#L46), you can overwrite their values in variables-template.yml by specifying them in the variable groups.
* for the ML variables that need to change for experimentations, define them as [ML pipeline variables](../samples/image-classification-tensorflow/ml_service/pipelines/build_training_pipeline.py#L46). The defaults for ML variables are stored in [ml_model/parameters.json](../samples/image-classification-tensorflow/ml_model/parameters.json) so that they can run in DevOps pipelines [without having to be specified in the pipeline yamls](../samples/image-classification-tensorflow/devops_pipelines/03-train-evaluate-register-model.yml#L119).
