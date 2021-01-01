Data processing[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/image-classification-tensorflow/02-preprocess-data?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=33&branchName=main)
Model training[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/image-classification-tensorflow/03-train-evaluate-register-model?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=37&branchName=main)
Deploy and smoke test[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/image-classification-tensorflow/04-deploy-model-aci?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=39&branchName=main)

This sample differs from MLOpsPython in the following ways:

* It supports image data instead of tabular data.
* It uses Tensorflow/Keras for model training instead of scikit learn.
* It has a separate data processing pipeline from the model training pipeline.
* It doesn't have batch scoring, A/B testing, or canary deployment.

# Dataset Management
* The data processing pipeline uses a pre-registered dataset name and datastore name.
* To allow the pipeline to run on updated data without any code change, and to track the version of the data during each run, it takes a folder name as its parameter. The folder name can't be determined at pipeline publishing time. It must be determined during a run.
* When the folder name parameter is specified for a run, a new version of the dataset is registered and the folder is mounted. When this parameter is empty, the latest version of the dataset is used.