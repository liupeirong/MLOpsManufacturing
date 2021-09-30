# Simple Classifier Model <!-- omit in toc -->

This project contains the machine learning code required for training the sample model.

The `model` folder creates a dataset, trains a model, and saves the model as a pickle file.
You can run this folder by using the [getting started](#getting-started) section below.

## Sections <!-- omit in toc -->

- [Getting started](#getting-started)
- [Model files](#model-files)
  - [main.py](#mainpy)
  - [register_model.py](#register_modelpy)

## Getting started

The following describes how to run the `simple_classifier` model.

1. Navigate into `model` folder.

1. Create a virtual environment using `python -m venv venv` and activate the virtual environment.

1. Install requirements with `pip install -r requirements.txt`.

1. Run the following command to create the dataset

   - `python -m create_dataset --output-folder './dataset'`

1. Run the following for each training script:

   - `python -m main --data-folder './dataset' --output-folder './output_model'`
   - `python -m register_model --data-folder './output_model' --model-name 'simple_classifier'`

## Model files

There are multiple python scripts associated with the model training. Below are descriptions of the actions executed within each step.

### main.py

This script is for the actual training of the model.
This script loads in the training and test data created by `create_dataset.py` and `dataloader.py`
The model is trained on training data and is validated using the test data.
The model is written to the `output-folder`.

### register_model.py

This script is to copy the required model files for inferencing and register the model as a single package in Azure ML model registry.
