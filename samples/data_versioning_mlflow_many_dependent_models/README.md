For infrastructure setup, data preparation, please refer to the [DataOps Github Repository](https://github.com/Azure-Samples/modern-data-warehouse-dataops/e2e_samples), under directory `dataset_versioning`.

# Overview

The sample *Databricks* notebook demonstrates how to use [MLflow](https://mlflow.org/) to track data versioning with [DeltaLake](https://docs.microsoft.com/en-us/azure/databricks/delta/delta-intro) and how to track many dependent models using MLFlow. It is developed based on the [Databricks sample notebook](https://docs.databricks.com/_static/notebooks/mlflow/mlflow-delta-training.html) using [Lending Club Loan Dataset hosted on Kaggle](https://www.kaggle.com/husainsb/lendingclub-issued-loans?select=lc_loan.csv). We provide an HTML version for a quick preview (you can also direct import the HTML version to Databricks).

__What does this sample demonstrate__:

* Track ML experimentation and model performance using MLFlow on Databricks, and trace back to the training dataset version.
* Access data using credential passthrough on Databricks (note, Databricks Premium is required).
* Use delta format tabular data for training.
* Manage dependent models using MLFlow, in this sample, a logistic regression and its dependent LIME model.

__What this sample does not demonstrate__:

* Comprehensive unit and integration tests - this sample doesn't have the level of unit tests or integration tests adequate for production deployment yet. 
* Production scale inferencing - this sample stops at experimentation level.
* End-to-end data and infrustructure pipelines. Please refer to `dataset_versioning` in [DataOps Github Repository](https://github.com/Azure-Samples/modern-data-warehouse-dataops/e2e_samples) for the end-to-end DataOps process, including infrastructure setup, data pipeline setup, data copying, security setup etc.

**Pipeline Structure**  
This example assumes a scenario where experiments are conducted on Databricks using delta format data. It also assumes that more than one model is required in the experiments and the models are dependent. In this case, it shows how to train a logistic regression model and a LIME model to explain it.

The sample notebook includes the following steps:
- Load data from DeltaLake, with specific version.
- Preproecss data and some featurization steps, using the same way shown in [this notebook](https://docs.databricks.com/_static/notebooks/mlflow/mlflow-delta-training.html).
- Train a Logistic Regression model using mllib and its dependent LIME model using [MMLSpark](https://github.com/Azure/mmlspark). Meanwhile, track the dataset version, the performance of the Logistic Regression Model, LIME model and related parameters using MLFlow.
- Demonstrate how to manage and copy dependent models to a specified storage account.




# Getting Started


## DevOps and DataOps

Please refer to `data versioning` in [DataOps Repository](https://github.com/Azure-Samples/modern-data-warehouse-dataops/tree/master/e2e_samples) for:

- Setup infrastructure on Azure
  - Setup Databricks instances
  - Create Azure DataLake Gen 2 storage account, and related security setup.
  - Keyvault
  - Azure Data Factory

- Security setup 
  - (Optional) Credential passthrough. If credential passthrough is desired, please make sure Databricks premium is used and Databricks clusters need to be created *for each user*, since it replies on AAD.
  - Secret scope. Using secret scope to access the storage account is a classic way.

- Dataset download and setup
  - Data ingestion to simulate multiple versions in DeltaLake.
  - If not using credential passthrough to access the storage account, you need to mount the corresponding container to the databricks filesystem, e.g. `/mnt/datalake`.
  
## Cluster Configuration
This sample requires running remotely on Databricks cluster, please refer to the "cluster configuration" in the `loan_classification.ipynb`.
