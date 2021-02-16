# Overview

## Background

When you creating a unit test which is using [AML SDK](https://docs.microsoft.com/en-us/python/api/overview/azure/ml/?view=azure-ml-py), you need to mock a lot of classes.
Also if you write multiple test codes without using fixtures, there will be a lot of duplicate code. The above problems can be solved simply by including a pre-made AML fixture file to your code.

## Folder Structure

This folder contains [pytest-fixture](https://docs.pytest.org/en/stable/fixture.html) templates for reuse in new MLOps projects on [Azure Machine Learning Service](https://azure.microsoft.com/en-us/services/machine-learning/).
```bash
├─ README.md # explains how to use AML fixtures 
├─ test_aml_mock_fixtures_default.py # AML fixtures which is not using env util
└─ test_aml_mock_fixtures_env.py # # AML fixture which is using env util
```

## Getting Started

This tutorial explains how to use AML fixture with your code.   By including this python file in your code, this file will set mocks for AML SDK related to AML Pipeline build scripts:

* Workspace.Get
* PythonScriptStep
* Pipeline
* Pipeline.publish
* ComputeTarget (AmlCompute only)
* Environment

### Fixture for mocking AML SDK

> [This fixture](./test_aml_mock_fixtures_default.py) is **independent** from other utils and tools used in
[samples](/samples) of this repo.

This fixture is for the case of referencing environment variables directly without using env util.

1. Import [./test_aml_mock_fixtures_default.py](./test_aml_mock_fixtures_default.py) under your tests directory

1. Import predefined fixture to your test method
    ```
    from test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks
    ```
    > Note: Depending on the location you are referencing 'test_aml_mock_fixtures_env', the path may need to be different.

1. Pass 'aml_pipeline_mocks' as parameter to your unit test method
    ```
    [Example]
    def test_build_data_processing_os_cmd_pipeline(aml_pipeline_mocks):
    ```

1. Load mocks from fixture using tuple
    ```
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
    aml_pipeline_mocks
    ```
    
1. Use "spy" to write tests in more detail

    ```
    [Example]
    # Create a spy
    spy_pythonscriptstep_create =\
        mocker.patch('azureml.pipeline.steps.PythonScriptStep',wraps=PythonScriptStep)

    # Check if PythonScriptStep instantiation was called correctly
    spy_pythonscriptstep_create.\
        assert_called_once_with(allow_reuse=False,
                                runconfig=ANY,
                                arguments=ANY,
                                source_directory=e.sources_directory_train,
                                script_name="preprocess/"
                                            "preprocess_os_cmd_aml.py",
                                name="Preprocess Data with OS cmd",
                                compute_target=ANY)
    ```

    The full unit test code can be found at [test_build_data_processing_os_cmd_pipeline.py](/samples/non-python-preprocess/ml_service/tests/pipelines/test_build_data_processing_os_cmd_pipeline.py).

### Fixture for mocking AML SDK with Env util

> [This fixture](./test_aml_mock_fixtures_env.py) is **dependent on the ml_service.util.env_variables.Env class**
used in [non-python-preprocess sample](/samples/non-python-preprocess/ml_service/util/env_variables.py).

This fixture is for the case of referencing environment variables using env util.

### How to use

TODO

## Limitations

This fixture is still working in progress and ot 100% support for the AML SDK. If you have any fixtures that you would like to have, or if you find improvements while using them, please leave them in the issues.
