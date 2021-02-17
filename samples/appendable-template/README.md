# Overview

__What does this sample demonstrate__:

* Use "Appendable Template" when building Azure ML pipelines.

__What doesn't this sample demonstrate__:

* E2E MLOps lifecycle.

## Appendable Template

In Azure ML, a ML `model` comes from a training `experiment` which consists of multiple `runs`. One type of `run` is an Azure ML `pipeline` run which also consists of multiple `steps` or child runs.

The way provided by the Azure ML SDK for Python to build/publish Azure ML pipelines is a Python script invoking Azure ML SDK methods. This is a simple example
) of building an Azure ML pipeline with Azure ML SDK for Python (taken from [`diabetes_regression_build_train_pipeline.py`](https://github.com/microsoft/MLOpsPython/blob/master/ml_service/pipelines/diabetes_regression_build_train_pipeline.py) in `MLOpsPython` repo).

```python
    train_step = PythonScriptStep(
        name="Train Model",
        script_name=e.train_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        outputs=[pipeline_data],
        arguments=[
            "--model_name",
            model_name_param,
            "--step_output",
            pipeline_data,
            "--dataset_version",
            dataset_version_param,
            "--data_file_path",
            data_file_path_param,
            "--caller_run_id",
            caller_run_id_param,
            "--dataset_name",
            dataset_name,
        ],
        runconfig=run_config,
        allow_reuse=True,
    )

    register_step = PythonScriptStep(
        name="Register Model ",
        script_name=e.register_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        inputs=[pipeline_data],
        arguments=["--model_name", model_name_param, "--step_input", pipeline_data, ],  # NOQA: E501
        runconfig=run_config,
        allow_reuse=False,
    )

    register_step.run_after(train_step)
    steps = [train_step, register_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline._set_experiment_name
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id,
    )
```

"Appendable Template" is a best practice way of streamline or code style these Azure ML pipeline build scripts. With "Appendable Template", you can:

- Encapsulate Azure ML pipeline steps as classes
- Easily append them to an Azure ML pipeline in a structured way

In "Appendable Template", you need to create classes for pipeline steps, and use them to build an Azure ML pipeline. This is an example of building an Azure ML pipeline with "Appendable Template".

```python
    train_step = TrainStep(workspace=aml_workspace, env=e,
                           compute=aml_compute, config=run_config,
                           pipeline_parameters=pipeline_parameters,
                           output_pipelinedata=pipeline_data)
    train_step.append_step(steps)

    register_step = RegisterStep(workspace=aml_workspace, env=e,
                                 compute=aml_compute, config=run_config,
                                 pipeline_parameters=pipeline_parameters,
                                 input_pipelinedata=pipeline_data)
    register_step.append_step(steps)

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline._set_experiment_name
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id,
    )
```

This is an example of a class for a pipeline step. This class encapsulates details of a pipeline step. When multiple developers work on multiple pipeline steps, each developer can work on a specific class for a pipeline step they are working on independently, instead of working on a single script (which leads to merge conflicts).

```python
from azureml.pipeline.steps import PythonScriptStep


class TrainStep:
    def __init__(self, workspace, env, compute, config, pipeline_parameters,
                 output_pipelinedata):
        self.workspace = workspace
        self.env = env
        self.compute = compute
        self.config = config
        self.pipeline_parameters = pipeline_parameters
        self.output_pipelinedata = output_pipelinedata

    def append_step(self, step_list):
        train_step = PythonScriptStep(
            name="Train Model",
            compute_target=self.compute,
            source_directory=self.env.sources_directory_train,
            script_name=self.env.train_script_path,
            outputs=[self.output_pipelinedata],
            arguments=[
                "--model_name",
                self.pipeline_parameters["model_name"],
                "--step_output",
                self.output_pipelinedata,
                "--dataset_version",
                self.pipeline_parameters["dataset_version"],
                "--data_file_path",
                self.pipeline_parameters["data_file_path"],
                "--caller_run_id",
                self.pipeline_parameters["caller_run_id"],
                "--dataset_name",
                self.env.dataset_name,
            ],
            runconfig=self.config,
            allow_reuse=True,
        )

        if len(step_list) > 0:
            previous_step = step_list[-1]
            train_step.run_after(previous_step)

        step_list.append(train_step)
```

# Getting Started

## Modification

This sample is based on `diabetes_regression` sample in [`MLOpsPython` repo](https://github.com/microsoft/MLOpsPython/). 

This sample contains minimum files required to run `diabetes_regression_build_train_pipeline.py` locally to build an Azure ML pipeline.

`diabetes_regression_build_train_pipeline_appendable.py` is a modified version of original `diabetes_regression_build_train_pipeline.py`. It supports "Appendable Tempalte".

Three new classes for pipeline steps are added to `ml_service/pipelines/steps` directory.

- `diabetes_regression_build_evaluate_steps.py`
- `diabetes_regression_build_register_steps.py`
- `diabetes_regression_build_train_steps.py`

## Prerequisite for local run

1. Follow ["Development environment setup"](https://github.com/microsoft/MLOpsPython/blob/master/docs/development_setup.md) in `MLOpsPython` repo.

## Running locally

1. [Create an Azure ML workspace](https://docs.microsoft.com/en-us/azure/machine-learning/concept-workspace#-create-a-workspace) in your Azure subscription.

2. Make a copy of [.env.example](local_development/.env.example), place it in the root of this sample, configure the variables, and rename the file to `.env`. You need to configure `SUBSCRIPTION_ID`, `RESOURCE_GROUP` and `WORKSPACE_NAME`.

3. Run `diabetes_regression_build_train_pipeline.py` or `diabetes_regression_build_train_pipeline_appendable.py` from `samples/appendable-template` directory.

```bash
export BUILD_BUILDID=$(uuidgen)
python ml_service/pipelines/diabetes_regression_build_train_pipeline_appendable.py
```

4. In [Azure ML studio](https://ml.azure.com/), click "Pipelines" menu, click "Pipeline endpoints" tab, click the pipeline endpoint you published, and click "Submit" button.

5. In "Set up pipeline run" dialog, select an existing experiment, or create a new experiment, and click "Submit" button.

6. In the pipeline endpoint page, click "Runs" tab, and click the pipeline run you submitted.

## CI/CD in Azure DevOps

1. Clone `MLOpsPython` repo

2. Delete the original `diabetes_regression_build_train_pipeline.py` in `ml_service/pipelines` directory of `MLOpsPython` repo.

3. Copy `diabetes_regression_build_train_pipeline_appendable.py` to `ml_service/pipelines` directory of `MLOpsPython` repo, and rename it to `diabetes_regression_build_train_pipeline.py`.

4. Copy three new classes for pipeline steps to `ml_service/pipelines/steps` directory of `MLOpsPython` repo.

5. Follow ["Getting Started with MLOpsPython"](https://github.com/satonaoki/MLOpsPython/blob/master/docs/getting_started.md).
