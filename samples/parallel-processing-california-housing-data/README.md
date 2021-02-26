# Overview

**What does this sample demonstrate:**
- A simple example of how to use `ParallelRunScript` to process data in parallel.
- Sample data is created based on california housing dataset obtained by `sklearn.datasets.fetch_california_housing` function. For more details please refer to sklearn documentation [Real world dataset - 7.2.7. California Housing dataset](https://scikit-learn.org/dev/datasets/real_world.html#california-housing-dataset)

    > According to above documentation,  
    > "This dataset was obtained from the StatLib repository. http://lib.stat.cmu.edu/datasets/"

    > References  
    > Pace, R. Kelley and Ronald Barry, Sparse Spatial Autoregressions, Statistics and Probability Letters, 33 (1997) 291-297

**What doesn't this sample demonstrate**:
- any tests
- any CI/CD
- no dataset is used

**Pipeline Structure**  
This example assumed a scenario that an Azure Machine Learning service pipeline was used to train a simple linear regression model based on california housing data. 

Three steps are included:
- preparation step, which downloaded raw text files from datastore.
- extraction step, a `ParallelRunStep` which extracted data from the text files and merge the data to a single file.
- training step, which trained a simple linear regression model used the data obtained from extraction step.
    - please be noticed that `sklearn.linear_model.LinearRegression` is used to create the model. for details of sklearn's license, please check the [BSD 3-Clause License](https://github.com/scikit-learn/scikit-learn/blob/main/COPYING).



# Getting Started

- [Prerequisites](#Prerequisites)
- [Running locally](#Running-locally)
## Prerequisites
- [Create Azure Resources](#Create-Azure-Resources)
- [Prepare input data](#Prepare-input-data)
- [Add Azure ML compute, datastore](#Add-Azure-ML-compute-datastore)

### Create Azure Resources

1. Whether you run this project locally or in Azure DevOps CI/CD pipelines, the code needs to get Azure ML context for remote or offline runs. Create Azure resources as documented [here](../../common/infrastructure/README.md).

1. Review the folder structure explained [here](../../README.md#repo-structure).

### Prepare input data

This sample takes input files from Azure Machine Learning Datastore which mapped to Azure Blob Storage.

#### Create blob container and folders

1. Go to Azure Storage Account and create new container named 'azureml'

#### Upload input data

1. change directory to `data` and run `create_sample_data.py` to create sample data.
    ```
    cd samples/parallel-processing-california-housing/data
    python -m create_sample_data --count [count of text files(default 100)]
    ```
1. Upload the created files by adding 'input' directory in 'azureml' container.


### Add Azure ML compute, datastore and datasets

After you have all Azure resources and input data in Azure Storage, you need to create following Azure Machine Learning components.

- Azure Machine Learning compute
- Azure Machine Learning datastore

1. Change directory to samples/parallel-processing-california-housing.

    ```shell
    cd samples/parallel-processing-california-housing
    ```

1. Run following command to create compute.

    ```shell
    python -m environment_setup.provisioning.create-compute
    ```

1. Run following command to create datastore.

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
    |AML_COMPUTE_VM_SIZE|Azure Machine Learning compute virtual machine size. i.e. "STANDARD_D2_V2"|
    |AML_COMPUTE_IDLE_TIME|Azure Machine Learning compute idle time (seconds) before scaling down|
    |AML_COMPUTE_MIN_NODES|Azure Machine Learning compute minimum nodes number|
    |AML_COMPUTE_MAX_NODES|Azure Machine Learning compute maximum nodes number|
    |AML_BLOB_DATASTORE_NAME| Azure Machine Learning blob datastore name|
    |AML_STORAGE_ACCOUNT_NAME| Azure Storage Account name for Azure Machine Learning blob datastore|
    |AML_BLOB_CONTAINER_NAME | Blob container name which contains input data|
    |AML_STORAGE_ACCOUNT_KEY |Azure Storage Account Key|
    |PIPELINE_ENDPOINT_NAME| Azure Machine Learning pipeline endpoint name|
    |PIPELINE_NAME| Azure Machine Learning pipeline name|
    |INPUT_DIR| folder name which is used to save input files. Don't change this value.|
    |SOURCES_DIR_TRAIN|source code directory for Azure Machine Learning pipeline|
    |PREPARATION_STEP_SCRIPT_PATH| python script path for the preparation step|
    |EXTRACTION_STEP_SCRIPT_PATH| python script path for the extraction step|
    |TRAINING_STEP_SCRIPT_PATH| python script path for the training step|
    |ERROR_THRESHOLD|The number of record failures for TabularDataset and file failures for FileDataset that should be ignored during processing. If the error count goes above this value, then the job will be aborted.|
    |NODE_COUNT|Number of nodes in the compute target used for running the Parallel Run|
    |MINI_BATCH_SIZE|size of data can be processed in one run() call|
    |PROCESS_COUNT_PER_NODE|Number of processes executed on each node. Optional, default value is number of cores on node|
    |RUN_INVOCATION_TIMEOUT|Timeout in seconds for each invocation of the run() method|
    

1. Use the VSCode [dev container](./.devcontainer), or install Anaconda or Mini Conda and create a Conda envrionment by running [local_install_requirements.sh](./local_development/local_install_requirements.sh).

1. In VSCode, open the root folder of this sample, select the Conda environment created above as the Python interpretor.

1. Publish and run Azure ML pipelines. 
    - To publish and run Azure ML pipelines, run:
        ```shell
        # publish the Azure ML pipeline
        python -m ml_service.pipelines.build_pipeline
        ```

# Linting

## Flake8

This sample uses [Flake8](https://flake8.pycqa.org/en/latest/) as linting tool. Ideally we should do linting for all python code, however we exclude Kaldi sample source code as it comes from another repo. This happens a lot in real project that some code comes from outside of the project and you don't want to modify the code. 

See [.flake8](./.flake8) for rule settings.

