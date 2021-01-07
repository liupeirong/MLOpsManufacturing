# Overview

The samples in this project are intended for providing a starting point for building ML solutions with MLOps practices. They are meant to represent different frameworks such as Tensorflow or Yolo, different scenarios such as model training in the cloud or influencing on the edge, or how certain technologies are used such as mocking Azure ML SDK for unit testing or leveraging observability library to send logs and metrics to different destinations.  

Each sample has a README that details what it's meant to demonstrate. Below is a quick index -

- [Image classification with Tensorflow and Keras](mage-classification-tensorflow) demonstrates how to use Azure DevOps and Azure ML to build, train, evaluate, and track models, including how to retrain on new data. 
- [Run non-Python code as a step in ML Pipeline](non-python-preprocess) demonstrates how to run non Python custom code as a step in Azure ML pipelines. We've seen many cases where companies already have custom code they use to preprocess data before training a ML model. This sample also demonstrates how to use PyTest to mock Azure ML SDK for unit testing.
