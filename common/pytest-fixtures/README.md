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

This tutorial explains how to use AML fixture with your code with this [sample](/samples). By including this python file in your code, this will set the following AML SDK mocks:

* Workspace.Get
* PythonScriptStep
* Pipeline
* Pipeline.publish
* ComputeTarget (AmlCompute only)

### Fixture for mocking AML SDK

> [This fixture](./test_aml_mock_fixtures_default.py) is **independent** from other utils and tools used in
[samples](/samples) of this repo.

This code is for cases not using env util.

1. Copy and paste this [./test_aml_mock_fixtures_default.py](./test_aml_mock_fixtures_default.py) file under your tests directory

    This code mocks frequently used objects in AML SDK and returns them as fixtures so that they can be reused in other code.

1. Import predefined fixture to your test code

    ```python
    from ml_service.tests.pipelines.test_aml_mock_fixtures_default import aml_pipeline_mocks
    ```

    > Note: Depending on the location you are referencing the fixture file, this path 'ml_service.tests.pipelines.test_aml_mock_fixtures_default' may need to be different.

1. Pass 'aml_pipeline_mocks' as a parameter to your unit test code and load mock objects from fixture by referencing the code below.

    ```python
    def test_build_data_processing_os_cmd_pipeline_happy_path(mocker: MockFixture, aml_pipeline_mocks):  
    
    # Load mocks from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks
    ```

    Each mock object can be accessed by listing them again cause it uses tuple notation.

1. Assertion using mocks

    ```python
    # Check if the correct workspace retrieved
    mock_workspace_get.assert_called_with(name=workspace_name,
                                          resource_group=resource_group,
                                          subscription_id=subscription_id)

    # Check if Pipeline publish was called with arguments
    mock_pipeline_publish.assert_called_once_with(name=preprocessing_pipeline_name,
                                                  description="Data preprocessing"
                                                              " OS cmd pipeline",
                                                  version=build_id)
    ```

    This code shows how to make an assertion using an imported mock objects. Parameters such as 'workspace_name', 'resource_group', 'subscription_id' are already defined in the fixture file.

    The full unit test code can be found at [test_build_data_processing_os_cmd_pipeline.py](/samples/non-python-preprocess/ml_service/tests/pipelines/test_build_data_processing_os_cmd_pipeline.py).

### Fixture for mocking AML SDK with Env util

> [This fixture](./test_aml_mock_fixtures_env.py) is **dependent on the ml_service.util.env_variables.Env class**
used in [non-python-preprocess sample](/samples/non-python-preprocess/ml_service/util/env_variables.py).

This fixture is for the case of referencing environment variables using env util.

1. Copy and paste this [./test_aml_mock_fixtures_env.py](./test_aml_mock_fixtures_env.py) file under your tests directory

    This code mocks frequently used objects in AML SDK and returns them as fixtures so that they can be reused in other code.

1. Import predefined fixture to your test code

    ```python
    from ml_service.tests.pipelines.test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks
    ```

    > Note: Depending on the location you are referencing the fixture file, this path 'ml_service.tests.pipelines.test_aml_mock_fixtures_env' may need to be different.

1. Import environment variable util file

    ```python
    from ml_service.util.env_variables import Env
    ```

1. Pass 'aml_pipeline_mocks' as a parameter to your unit test code and load mock objects from fixture by referencing the code below.

    ```python
    def test_build_data_processing_os_cmd_pipeline_happy_path(mocker: MockFixture, aml_pipeline_mocks):  
    
    # Load mocks from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks
    ```

    Each mock object can be accessed by listing them again cause it uses tuple notation.

1. Assertion using mocks with environment variables

    ```python
    # Load Mocked environment variables
    e = Env()

    # Check if the correct workspace retrieved
    mock_workspace_get.assert_called_with(name=e.workspace_name,
                                          resource_group=e.resource_group,
                                          subscription_id=e.subscription_id)

    # Check if Pipeline publish was called with arguments
    mock_pipeline_publish.assert_called_once_with(name=e.preprocessing_pipeline_name,
                                                  description="Data preprocessing"
                                                              " OS cmd pipeline",
                                                  version=e.build_id)
    ```

    This code shows how to make an assertion using an imported mock objects with environment variables. Parameters such as workspace_name and resource_group can be accessed and used directly through the loaded environment variable object.

    The full unit test code can be found at [test_build_data_processing_os_cmd_pipeline.py](/samples/non-python-preprocess/ml_service/tests/pipelines/test_build_data_processing_os_cmd_pipeline.py).

## Limitations

This fixture is still working in progress and ot 100% support for the AML SDK. If you have any fixtures that you would like to have, or if you find improvements while using them, please leave them in the issues.
