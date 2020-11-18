from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core import Workspace, Datastore
from azureml.core.runconfig import RunConfiguration
from azureml.data import OutputFileDatasetConfig
from ml_service.util.attach_compute import get_compute
from ml_service.util.env_variables import Env
from ml_service.util.manage_environment import get_environment


def main():
    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group,
    )
    print(f"get_workspace:{aml_workspace}")

    # Get Azure machine learning cluster
    aml_compute = get_compute(aml_workspace, e.compute_name, e.vm_size)
    if aml_compute is not None:
        print(f"aml_compute:{aml_compute}")

    # Create a reusable Azure ML environment
    environment = get_environment(
        aml_workspace,
        e.aml_env_name,
        conda_dependencies_file=e.aml_env_train_conda_dep_file,
        create_new=e.rebuild_env,
    )  #
    run_config = RunConfiguration()
    run_config.environment = environment

    if e.datastore_name:
        datastore_name = e.datastore_name
    else:
        datastore_name = aml_workspace.get_default_datastore().name
    run_config.environment.environment_variables["DATASTORE_NAME"] = datastore_name  # NOQA: E501

    datastore = Datastore(aml_workspace, name=datastore_name)
    data_file_path_param = PipelineParameter(name="data_file_path", default_value=e.dataset_name)  # NOQA: E501
    preprocessing_param = PipelineParameter(name="preprocessing_param", default_value="")  # NOQA: E501

    # The version of the input/output dataset can't be determined at pipeline publish time, only run time.  # NOQA: E501
    # Options to store output data:
    # Option 1: Use blob API to write output data. Otherwise, no way to dynamically change the output dataset based on PipelineParameter, # NOQA: E501
    #     The following will not work. It generate a path like "PipelineParameter_Name:data_file_path_Default:gear_images"  # NOQA: E501
    #         output_dataset = OutputFileDatasetConfig(destination=(datastore, data_file_path_param))  # NOQA: E501
    #     This option means writing a file locally and upload to the datastore. Fewer dataset, more code.  # NOQA: E501
    # Option 2: Use a dynamic path in OutputFileDatasetConfig, and register a new dataset at completion  # NOQA: E501
    #     Output dataset can be mounted, so more dataset to maintain, less code.   # NOQA: E501
    # Using Option 2 below.
    output_dataset = OutputFileDatasetConfig(
        name=e.processed_dataset_name,
        destination=(datastore, "/dataset/{output-name}/{run-id}")
    ).register_on_complete(
        name=e.processed_dataset_name)

    preprocess_step = PythonScriptStep(
        name="Preprocess Data",
        script_name=e.preprocess_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--dataset_name", e.dataset_name,
            "--datastore_name", datastore_name,
            "--data_file_path", data_file_path_param,
            "--output_dataset", output_dataset,
            "--preprocessing_param", preprocessing_param
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Preprocess created")

    steps = [preprocess_step]
    preprocess_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    preprocess_pipeline._set_experiment_name
    preprocess_pipeline.validate()
    published_pipeline = preprocess_pipeline.publish(
        name=e.preprocessing_pipeline_name,
        description="Data preprocessing pipeline",
        version=e.build_id,
    )
    print(f"Published pipeline: {published_pipeline.name}")
    print(f"for build {published_pipeline.version}")


if __name__ == "__main__":
    main()
