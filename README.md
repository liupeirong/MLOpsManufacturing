Data Processing Pipeline: [![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsTensorflow/_apis/build/status/02-processing-data?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsTensorflow/_build/latest?definitionId=17&branchName=main)
Model Training Pipeline: [![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsTensorflow/_apis/build/status/03-train-evaluate-register-model?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsTensorflow/_build/latest?definitionId=18&branchName=main)
Deployment Pipeline: [![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsTensorflow/_apis/build/status/04-deploy-model-aci?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsTensorflow/_build/latest?definitionId=19&branchName=main)

# Overview

This project is based on and inspired by [MLOpsPython](https://github.com/microsoft/MLOpsPython).  It differs from MLOpsPython in the following ways:

* It supports image data instead of tabular data.
* It uses Tensorflow/Keras for model training instead of scikit learn.
* It has a separate data processing pipeline from the model training pipeline.
* It doesn't have batch scoring, A/B testing, or canary deployment.
