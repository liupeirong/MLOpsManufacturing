from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, StepSequence
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import OutputFileDatasetConfig
from azureml.core import Dataset, Experiment
import utils.settings as env
from utils.workspace import get_workspace_configs

source_directory = '../model'
training_data_path = 'data/training_data.csv'
testing_data_path = 'data/test_data.csv'
model_output_path = 'model/'
train_model_path = 'main.py'
register_model_script_path = 'register_model.py'
pip_requirements_path = 'requirements.txt'


def get_configs():

    # Get workspace configs
    workspace, compute_target, datastore, run_config = get_workspace_configs(
        name=env.workspace_name,
        workspace_resource_group=env.workspace_resource_group,
        datastore_resource_group=env.datastore_resource_group,
        subscription_id=env.subscription_id,
        tenant_id=env.tenant_id,
        app_id=env.app_id,
        app_secret=env.app_secret,
        compute_target_name=env.compute_target_name,
        datastore_name=env.datastore_name,
        datastore_container_name=env.datastore_container_name,
        data_storage_account_name=env.data_storage_account_name,
        data_storage_account_key=env.data_storage_account_key,
        environment_name=env.environment_name,
        environment_version=env.environment_version,
        environment_base_image=env.environment_base_image,
        environment_pip_requirements_path=pip_requirements_path,
    )

    training_dataset = Dataset.Tabular.from_delimited_files(
        path=(datastore, training_data_path), validate=False, include_path=True
    )
    test_dataset = Dataset.Tabular.from_delimited_files(
        path=(datastore, testing_data_path), validate=False, include_path=True
    )

    training_ds_consumption = DatasetConsumptionConfig("training_dataset", training_dataset)
    test_ds_consumption = DatasetConsumptionConfig("test_dataset", test_dataset)

    model_output_dir = OutputFileDatasetConfig(
        name='model_output_dir',
        destination=(datastore, model_output_path)).as_upload()

    train_model_step = PythonScriptStep(
        script_name=train_model_path,
        source_directory=source_directory,
        arguments=[
            '--output-folder', model_output_dir
        ],
        inputs=[training_ds_consumption, test_ds_consumption],
        compute_target=compute_target,
        runconfig=run_config,
        allow_reuse=True
    )
    register_model_step = PythonScriptStep(
        script_name=register_model_script_path,
        source_directory=source_directory,
        arguments=[
            '--data-folder', model_output_dir.as_input(),
            '--model-name', env.model_name,
            '--build-id', env.build_id,
            '--build-source', env.build_source
        ],
        compute_target=compute_target,
        runconfig=run_config,
        allow_reuse=True
    )

    pipeline_steps = StepSequence(
        steps=[
            train_model_step,
            register_model_step
        ]
    )

    # Get pipeline
    pipeline = Pipeline(
        workspace=workspace,
        steps=pipeline_steps
    )
    pipeline.validate()

    return workspace, pipeline


if __name__ == "__main__":
    # note this only needs to be done once

    workspace, pipeline = get_configs()
    pipeline.publish(name=env.aml_pipeline_name)
    pipeline_run1 = Experiment(workspace, 'Train_Model').submit(pipeline)
    pipeline_run1.wait_for_completion()
