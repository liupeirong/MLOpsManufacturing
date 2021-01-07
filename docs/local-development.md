# Problem Statement
When you train a machine learning model in an Azure Machine Learning (AML) cluster, with or without AML pipelines, debugging can be challenging because part of the code runs on a remote machine. You could train models locally with AML SDK, but the code and behavior for local runs are not exactly same as remote runs. In this article, we describe a few scenarios of how to be productive when developing AML solutions locally.

> Note: the best tool for AML local development is probably [Azure Machine Learning VSCode extention](https://docs.microsoft.com/en-us/azure/machine-learning/tutorial-setup-vscode-extension). At the time of this writing, version 0.6.19 doesn't work on a Ubuntu machine or a Windows machine remote SSH into Ubuntu.

# Scenario 1: Separate code without remote dependency if possible
If the code can run entirely locally without having to communicate with a remote service or cluster, then you can debug it as usual. 

For example, in the `image-classification-tensorflow` sample, [train.py](../samples/image-classification-tensorflow/ml_model/train/train.py) contains code to split the data for training and testing and train the model. It depends on Keras but not a remote service or cluster. Meanwhile [train_aml.py](../samples/image-classification-tensorflow/ml_model/train/train_aml.py) accesses Azure ML Datastore and Dataset. You can debug `train.py` without any special setup.

You could still debug code that has remote dependency as [documented for that sample](../samples/image-classification-tensorflow#running-locally). However, if the code doesn't fully support local run, it will run into errors that don't happen in remote run.

# Scenario 2: Run AML experiment locally to train models with Azure ML SDK - Offline Run
Azure ML supports [local compute target for both training and inferencing](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-attach-compute-targets#local). Here is [an example](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/training/train-on-local/train.py) to train a scikit-learn model locally using Azure ML SDK. Most of the code remain common for both local and remote training. However, local runs have limitations, for example:
1. can't run AML pipelines locally
2. can't mount AML Datastore or Datasets locally
3. local run doesn't have context such as a parent or child

# Scenario 3: Trigger AML experiment or pipeline runs in a remote cluster from local machine
You can trigger an AML experiment to run remotely from a local machine, or you can trigger an AML pipeline which only runs in AML compute cluster. For example, to publish the data preprocessing pipeline in the `image-classification-tensorflow` sample:
1. In a terminal, activate the Conda environment and go to the root directory of the sample
2. Ensure the variables for AML are set correctly in your local `.env`
3. Place a breakpoint in [build_data_processing_pipeline.py](../samples/image-classification-tensorflow/ml_service/pipelines/build_data_processing_pipeline.py), run
    ```bash
    python -m debugpy --listen 5678 --wait-for-client ml_service/pipelines/build_data_processing_pipeline.py
    ```
4. In VSCode, create a launch configuration to attach to the debugger, and F5:
    ```json
    "configurations": [
      {
        "name": "Python: Attach",
        "cwd": "${workspaceFolder}/samples/image-classification-tensorflow",
        "type": "python",
        "request": "attach",
        "connect": {
          "host": "localhost",
          "port": 5678
        },
      }
    ]
    ```
5. Place a breakpoint in [run_data_processing_pipeline.py](../samples/image-classification-tensorflow/ml_service/pipelines/run_data_processing_pipeline.py), run
    ```bash
    python -m debugpy --listen 5678 --wait-for-client ml_service/pipelines/run_data_processing_pipeline.py --aml_pipeline_name flower-data-processing-pipeline
    ```

You can modify the code to supply additional AML pipeline parameters as shown in [this example](../samples/image-classification-tensorflow/ml_service/pipelines/run_training_pipeline.py#L56). 

# Scenario 4: Use a dev VM as AML compute cluster for training to shorten startup time
This scenario is not about local debugging, however, it could also help to make development more productive. When you train remotely in an AML compute cluster, the cluster automatically scales down when idle, it might take a while for the cluster to spin up everytime you submit a run. You can reduce this spin up time by [attaching your own VM](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-attach-compute-targets). If you use a VM for development, it's already running anyways, saving cost and time.

If you attach your own VM, you probably want to configure Conda and Docker to store environments and images on an attached data disk rather than OS disk because the OS disk is typically small. Additionally, AML pulls down environments in `~/.azureml`, link this directory to a data disk as well.
