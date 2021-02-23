# Overview

A lot of ML models and datasets are uploaded and managed using [Azure Machine Learning Service](https://azure.microsoft.com/en-us/services/machine-learning/). It can be effectively managed by adding meta information using [tags](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.data.abstract_dataset.abstractdataset?view=azure-ml-py#add-tags-tags-none-) in ml model and dataset.
Such as tracking of used datasets within the automated processing of data, model creation and deployment (intermediate) datasets need to be tagged with metainformation about data quality, content, run in which they were generated and other data to identify or exclude them as candidates for a training run or for a easier review if quality of the model is not as expected.
However, Azure Machine Learning Service portal currently does not provide a ui that can check a specific dataset or ml model using tag information. There was a request from a customer who wanted to search dataset or ML model using tag information conveniently. This jupyter notebook was created to support this kinds of request.

## How it works?

The idea of this Jupyter notebook is as follows. Load the Azure ML workspace and dataset into memory using Azure ML Python SDK. Then, using the Pandas dataframe, you can search for the tag that meets the conditions.


