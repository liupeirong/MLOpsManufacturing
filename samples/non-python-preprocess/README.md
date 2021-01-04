[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/non-python-preprocess/03-custom-process-data-os-cmd?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=38&branchName=main)

# Overview

__What does this sample demonstrate__:

* Run non Python tool to process Azure ML Datasets as a step in Azure ML pipeline, check return code and capture stdout. 
* Create tests by mocking Azure ML SDK.

__What doesn't this sample demonstrate__:

* ML model training or deployment.

## Run non Python tools to preprocess data as a step in Azure ML pipeline

This [wrapper script](ml_model/preprocess/preprocess_os_cmd_aml.py) calls the command line command. In the basic sample it is just a `cp` to move data from the input folder to the output folder of its AML pipeline step.

```python
process = subprocess.Popen(['cp',
                            '{0}/.'.format(mount_context.mount_point),
                            step_output_path, '-r', '-v'],
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
```

So it is possible to call any tool or program which can be executed on a ubuntu linux (which is the base image for AML pipeline steps). The tool(s) need to be installed in the [custom container image](ml_model/preprocess/Dockerfile). This Dockerfile is [used to build a Docker image in the Azure ML pipeline](ml_service/pipelines/build_data_processing_os_cmd_pipeline.py#L33).

It's important to know that the input folder is getting mounted within the wrapper script, so you can only work on the data after this code:

```python
mount_context = dataset.mount()
mount_context.start()
print(f"mount_point is: {mount_context.mount_point}")
```

The mount point or folder is stored in this attribute `mount_context.mount_point` and can be used in the command line call. Similarly the output folder for this step is stored in `step_output_path`.

### Example: Setup image preprocessing with ImageMagick

As an example on how to extend this template I will use this [blog post](https://vitux.com/how-to-resize-images-on-the-ubuntu-command-line/) about resizing images with [ImageMagick](https://imagemagick.org/index.php).

1. Adding ImageMagick to the **Dockerfile** for the custom preprocessing step
2. Change the command line call in the **Wrapper script**
3. Rebuilding, publish and run the **data_processing_os_cmd_pipeline**

__Adding ImageMagick to the Dockerfile for the custom preprocessing step__

Adding the installation instruction `apt-get install -y imagemagick && \` to the [Dockerfile](ml_model/preprocess/Dockerfile) just before `apt-get clean` is called:

```dockerfile
RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 && \
    apt-get install -y fuse && \
    apt-get install -y imagemagick && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
```

__Change the command line call in the Wrapper script__

>Assumption: Input pictures are all jpg and output pictures should be 100x100. Input dataset is <http://download.tensorflow.org/example_images/flower_photos.tgz>, only the subfolder `daisy` will be resized.

Changing the command to:

```python
process = subprocess.Popen(['convert',
                           '{0}/daisy/*.jpg'.format(mount_context.mount_point),
                           '-resize',
                           '100x100!',
                           '{0}/resized.jpg'.format(step_output_path)],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
```

## Unit test with Azure ML mocks
[test_fixtures.py](ml_service/tests/pipelines/test_fixtures.py) is an example of how to mock Azure ML SDK using `pytest_mock`. [test_build_data_processing_os_cmd_pipeline.py](ml_service/tests/pipelines/test_build_data_processing_os_cmd_pipeline.py) uses the mocks to unit test Azure ML pipeline code.

# Getting Started

## Prerequisite 
1. Whether you run this project locally or in Azure DevOps CI/CD pipelines, the code needs to get Azure ML context for remote or offline runs. Create Azure resources as documented [here](../../common/infrastructure/README.md). 
2. Review the folder structure explained [here](../../README.md#repo-structure).

## Running locally
1. Make a copy of [.env.example](local_development/.env.example), place it in the root of this sample, configure the variables, and rename the file to `.env`.
2. Use the VSCode [dev container](.devcontainer), or install Anaconda or Mini Conda and create a Conda envrionment by running [local_install_requirements.sh](local_development/local_install_requirements.sh).
3. In VSCode, open the root folder of this sample, select the Conda environment created above as the Python interpretor.
4. Publish and run Azure ML pipelines. Note that if you change the [Dockerfile](ml_model/preprocess/Dockerfile), set the variable `AML_REBUILD_ENVIRONMENT` in `.env` file to `true` for Azure ML to [build an updated image](ml_service/pipelines/build_data_processing_os_cmd_pipeline.py#L31).
    * To run the unit tests, open a terminal, activate the Conda environment for this sample, navigate to the root folder of this project, run
    ```bash
    python -m pytest 
    ```

    * To publish and run Azure ML pipelines, run:
    ```bash
    # publish the Azure ML pipeline
    python -m ml_service.pipelines.build_data_processing_os_cmd_pipeline
    # run the Azure ML pipeline
    python -m ml_service.pipelines.run_data_processing_pipeline --aml_pipeline_name "nonpython-data-preprocessing-pipeline" 
    ```

    * To debug, run:
    ```bash
    python -m debugpy --listen 5678 --wait-for-client ml_service/pipelines/build_data_processing_os_cmd_pipeline.py
    ```
    In VSCode, create a launch configuration to attach to the debugger, and F5:
    ```json
    "configurations": [
      {
        "name": "Python: Attach",
        "cwd": "${workspaceFolder}/samples/non-python-preprocess",
        "type": "python",
        "request": "attach",
        "connect": {
          "host": "localhost",
          "port": 5678
        },
      }
    ]
    ```

## CI/CD in Azure DevOps

1. Create an Azure DevOps variable group `nonpython-preprocess-aml-vg` that contains the following variables:

| name | description |
| --- | ---------- |
| AML_COMPUTE_CLUSTER_NAME | Azure ML Compute cluster used for training |
| RESOURCE_GROUP | Azure Resource Group where the Azure ML Workspace is located |
| WORKSPACE_NAME | Azure ML Workspace name |
| WORKSPACE_SVC_CONNECTION | Service Connection to Azure ML Workspace |

> Note that you can also overwrite the variables defined in [variables-template.yml](devops_pipelines/variables-template.yml) with the ones defined in this variable group. Variables defined in the variable group takes precedence over variables-template.yml because of [the order they are defined in Azure DevOps pipelines](devops_pipelines/03-custom-process-data-os-cmd.yml#L35). 

2. Create the build agent

The build agent needs to run linting, unit tests, and call Azure ML SDK to publish Azure ML pipelines to process the data. To create a Docker image for the build agent, create and run a build pipeline with [00-build-agent-pipeline.yml](devops_pipelines/build_agent/00-build-agent-pipeline.yml).

3. Create other pipelines

Create the remaining CI/CD pipelines defined in [devops_pipelines](devops_pipelines) folder. Verify or adjust their triggers if needed. By default, they are configured to trigger on pull requests or merging to main.
