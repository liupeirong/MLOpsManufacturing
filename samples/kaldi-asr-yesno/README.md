# Overview

The purpose of this sample is to demonstrate how to use Azure Machine Learning which requires additional software and dependencies, which could be non-python code, such as C++ source code, bash files and some binaries.


**What does this sample demonstrate:**
- Run [kaldi asr toolkit yesno sample](https://github.com/kaldi-asr/kaldi/tree/master/egs/yesno) in Azure Machine Learning pipeline.
- Create tests by mocking Azure ML SDK.

**What doesn't this sample demonstrate**:
- ML model deployment.

## Run kaldi sample in Azure ML pipeline

### Additional software for Azure ML pipeline
To run Kaldi sample, you need to have [Kaldi ASR Toolkit](https://github.com/kaldi-asr/kaldi) and its dependencies in compute cluster. Azure ML provides out of box environments as base image when you run Azure ML pipeline, but non of them include Kaldi ASR Toolkit.

Whenever you need additional software, you can create custom docker image and use it as custom base image. This sample demonstrate how you can provision and use custom image in Azure ML pipeline.

### Python wrapper for Azure ML pipeline
The [yesno sample](https://github.com/kaldi-asr/kaldi/tree/master/egs/yesno) uses bash script to train the model. However, Azure ML pipeline requires python code to execute steps. This sample demonstrate how you can write python wrapper code to run underline shell script as part of Azure ML pipeline step.

# Getting Started

- [Prerequisites](#Prerequisites)
- [Running locally](#Running-locally)
## Prerequisites

- [Create Azure Resources](#Create-Azure-Resources)
- [Build and push custom base image](#Build-and-push-custom-base-image)
- [Prepare input data](#Prepare-input-data)
- [Add Azure ML compute, datastore and datasets](#Add-Azure-ML-compute-datastore-and-datasets)

### Create Azure Resources

1. Whether you run this project locally or in Azure DevOps CI/CD pipelines, the code needs to get Azure ML context for remote or offline runs. Create Azure resources as documented [here](../../common/infrastructure/README.md).

1. Review the folder structure explained [here](../../README.md#repo-structure).

### Build and push custom base image

This sample requires Kaldi ASR Toolkit which is not avaiable for out of box Azure Machine Learning Environments. You can create custom docker images which contains all requires dependencies by yourself nad use it as Azure Machine Learning Environment. See [Create & use software environments in Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-environments) for more detail.

This sample contains [Dockerfile](./environment_setup/azureml_environment/Dockerfile) to build a custom base image which contains Kaldi ASR Toolkit and dependencies. Follow the steps below to build the image and push it to container registory. We recommend you to run separate VM which contains docker engine to build the image as it may take 30-60 minutes depending on specs.

1. Download SRILM from http://www.speech.sri.com/projects/srilm/download.html into environment_setup/azureml_environment folder and rename it to **srilm.tar.gz**.

1. Move to a directory which contains Dockerfile and build the docker image. This may take hours depending on computer spec. The [Dockerfile](./azureml_environment/Dockerfile) expects srilm.tar.gz file exists in the directory.

    ```shell
    docker build -t <your_acr_name>/<base_image_name>:<tag_name> .
    ```

1. Once the build has been completed, login to Azure Container Registry which you provisioned earlier.
    ```shell
    docker login -u <your_acr_username> -p <your_acr_password> <your_acr_login_server>
    ```

1. Then push the image to the registry.
    ```shell
    docker push <your_acr_name>/<base_image_name>:<tag_name>
    ```

1. Once the image has been pushed, update "image" section of [devcontainer.json](./.devcontainer/devcontainer.json) file.

### Prepare input data

This sample takes input and wave files from Azure Machine Learning Dataset which mapped to Azure Blob Storage.

#### Create blob container and folders

1. Go to Azure Storage Account and create new container named 'azureml'

#### Upload input data

1. Download files from https://github.com/kaldi-asr/kaldi/tree/master/egs/yesno/s5/input

1. Upload the downloaded files by adding 'input' directory in 'azureml' container.

#### Upload wave data

1. Download file from http://www.openslr.org/resources/1/waves_yesno.tar.gz and extract the downloaded file.

1. Upload all audio files by adding 'waves' directory in 'azureml' container.

As the sample obtain wave files from Azure Machine Learning Dataset, we commentted out run.sh where it downloads wave files.

### Add Azure ML compute, datastore and datasets

After you have all Azure resources and input data in Azure Storage, you need to create following Azure Machine Learning components.

- Azure Machine Learning compute
- Azure Machine Learning datastore and datasets

1. Change directory to samples/kaldi-asr-yesno.

    ```shell
    cd samples/kaldi-asr-yesno
    ```

1. Run following command to create compute.

    ```shell
    python -m environment_setup.provisioning.create-compute
    ```

1. Run following command to create datastore and dataset.

    ```shell
    python -m environment_setup.provisioning.create-datastore
    ```

## Running locally

1. Make a copy of [.env.example](./local_development/.env.example), place it in the root of this sample, configure the variables, and rename the file to .env.

1. Update variable values. 

    | name | description |
    |---|---|
    |SUBSCRIPTION_ID|Azure Subscription ID|
    |RESOURCE_GROUP| Azure Resource group name |
    |WORKSPACE_NAME| Azure Machine Learning workspace name|
    |AML_ENV_NAME| Azure Machine Learning Environment name|
    |AML_COMPUTE_CLUSTER_NAME| Azure Machine Learning compute cluster name|
    |AML_BLOB_DATASTORE_NAME| Azure Machine Learning blob datastore name|
    |AML_STORAGE_ACCOUNT_NAME| Azure Storage Account name for Azure Machine Learning blob datastore|
    |AML_BLOB_CONTAINER_NAME | Blob container name which contains input data|
    |AML_STORAGE_ACCOUNT_KEY |Azure Storage Account Key|
    |PIPELINE_ENDPOINT_NAME| Azure Machine Learning pipeline endpoint name|
    |PIPELINE_NAME| Azure Machine Learning pipeline name|
    |AML_INPUT_DATASET_NAME| input dataset name which is used by yesno sample. Don't change this value.|
    |AML_WAVES_DATASET_NAME| waves dataset name which is used by yesno sample. Don't change this value.|
    |SOURCES_DIR_TRAIN|source code directory for Azure Machine Learning pipeline|
    |FIRST_STEP_SCRIPT_PATH| python script path for the first step|
    |ACR_IMAGE| Custome base image name in Azure Container Registory|
    |ACR_ADDRESS| Azure Container Registory address|
    |ACR_USERNAME| Azure Container Registory user name|
    |ACR_PASSWORD| Azure Container Registory user password|

1. Use the VSCode [dev container](./.devcontainer), or install Anaconda or Mini Conda and create a Conda envrionment by running [local_install_requirements.sh](./local_development/local_install_requirements.sh).

1. In VSCode, open the root folder of this sample, select the Conda environment created above as the Python interpretor.

1. Publish and run Azure ML pipelines. 

    - To run the unit tests, open a terminal, activate the Conda environment for this sample, navigate to the root folder of this project, run
    ```shell
    python -m pytest 
    ```
    - To publish and run Azure ML pipelines, run:
    ```shell
    # publish the Azure ML pipeline
    python -m ml_service.pipelines.build_pipeline
    ```

## CI/CD in Azure DevOps

This sample contains Azure DevOps pipeline yaml files in devops_pipelines folder.

To use Azure DevOps pipeline, follow the steps below.

1. Create Service Connection for Azure Resourece Group.

1. Update values for yesno-variables-template.yml. Some variables are missing compare to .env file, as those values comes from Azure DevOps pipeline group and KeyVault.

1. Create aml-storage-account-key and acr-password as KeyVault secrets and save the corresponding values.

1. Create Azure pipeline by specifing yesno-ci.yml.

# Linting and Testing

## Flake8

This sample uses [Flake8](https://flake8.pycqa.org/en/latest/) as linting tool. Ideally we should do linting for all python code, however we exclude Kaldi sample source code as it comes from another repo. This happens a lot in real project that some code comes from outside of the project and you don't want to modify the code. 

See [.flake8](./.flake8) for rule settings.

## Pytest

This sample uses [pytest](https://docs.pytest.org/) for unit testing python code. We only test our code, and exlude kaldi sample source code.

[test_pipeline_utils.py](.\tests\ml_service\test_pipeline_utils.py) demonstrate how to mock Azure Machine Learning SDK and write unit test code.