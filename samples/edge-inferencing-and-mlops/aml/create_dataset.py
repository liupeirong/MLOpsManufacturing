from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, StepSequence
from azureml.data.output_dataset_config import OutputFileDatasetConfig
from azureml.core import Experiment
import utils.settings as env
from utils.workspace import get_workspace_configs

source_directory = '../model'
output_destination = '/data'
create_dataset_path = 'create_dataset.py'
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

    data_create_dataset_output_data = OutputFileDatasetConfig(
        name='data_create_dataset_output_data',
        destination=(datastore, output_destination)).as_upload()

    create_dataset = PythonScriptStep(
        script_name=create_dataset_path,
        source_directory=source_directory,
        arguments=[
            '--output-folder', data_create_dataset_output_data
        ],
        compute_target=compute_target,
        runconfig=run_config,
        allow_reuse=True
    )

    pipeline_steps = StepSequence(
        steps=[
            create_dataset
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
    pipeline_run1 = Experiment(workspace, 'Create_Dataset').submit(pipeline)
    pipeline_run1.wait_for_completion()
