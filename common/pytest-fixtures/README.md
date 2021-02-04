# Overview

This folder contains pytest-fixture templates for reuse in new MLOps projects.

* [Fixture for mocking AML SDK](##Fixture-for-mocking-AML-SDK)
* [Fixture for mocking AML SDK with Env util](##Fixture-for-mocking-AML-SDK-with-Env-util)

## Fixture for mocking AML SDK

[This fixture](./test_aml_mock_fixtures_default.py) is **independent** from other utils and tools used in
[samples](/samples) of this repo.

Sets mocks for AML SDK related to AML Pipeline build scripts:

* Workspace.Get
* PythonScriptStep
* Pipeline
* Pipeline.publish
* ComputeTarget (AmlCompute only)
* Environment

### How to use

1. Import libraries which helps AML mocking
    ```python3
    from pytest_mock import MockFixture
    from unittest.mock import ANY
    from ml_service.tests.pipelines.test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks  # NOQA: F401, E501
    from ml_service.util.env_variables import Env
    ```

1. Create a test function with MockFixture, aml_pipeline_mocks
    ```
    def test_build_data_processing_os_cmd_pipeline_happy_path(mocker: MockFixture,
                                                            aml_pipeline_mocks):
    ```

1. Load mocks using fixture
    ```
        # Load mocks from fixture
        # (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        #     aml_pipeline_mocks
    ```

1. Run main method usig runpy 
    ```
        # run as module (start from if __name__ == "__main__")
        runpy.run_module('ml_service.pipelines.'
                        'build_data_processing_os_cmd_pipeline',
                        run_name='__main__')
    ```

## Fixture for mocking AML SDK with Env util

[This fixture](./test_aml_mock_fixtures_env.py) is **dependent on the ml_service.util.env_variables.Env class**
used in [non-python-preprocess sample](/samples/non-python-preprocess/ml_service/util/env_variables.py).

Sets mocks for AML SDK related to AML Pipeline build scripts:

* Workspace.Get
* PythonScriptStep
* Pipeline
* Pipeline.publish
* ComputeTarget (AmlCompute only)
* Environment

### How to use

TODO
