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

TODO

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
