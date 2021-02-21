from azureml.core import Workspace, Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import Pipeline, PipelineEndpoint
from azureml.pipeline.core._restclients.aeva.models.error_response import ErrorResponseException
from azureml.pipeline.steps import PythonScriptStep
from datetime import datetime
from logging import getLogger, INFO, StreamHandler, Formatter
from ml_service.util.env_variables import Env
from ml_service.util.pipeline_utils import get_compute


def main():
    # Environment variables
    env = Env()

    # Azure ML workspace
    aml_workspace = Workspace.get(
        name=env.workspace_name,
        subscription_id=env.subscription_id,
        resource_group=env.resource_group,
    )
    logger.info(f"Azure ML workspace: {aml_workspace}")

    # Azure ML compute cluster
    aml_compute = get_compute(aml_workspace, env.compute_name)
    logger.info(f"Aazure ML compute cluster: {aml_compute}")

    # Azure ML environment
    environment = Environment(name=env.aml_env_name)
    conda_dep = CondaDependencies(conda_dependencies_file_path="./local_development/dev_dependencies.yml")
    environment.docker.enabled = True
    environment.docker.base_image = env.acr_image
    environment.docker.base_image_registry.address = env.acr_address
    environment.docker.base_image_registry.username = env.acr_username
    environment.docker.base_image_registry.password = env.acr_password
    environment.python.conda_dependencies = conda_dep

    run_config = RunConfiguration()
    run_config.environment = environment

    # List of pipeline steps
    step_list = list()
    first_step = PythonScriptStep(
        name="first_step",
        compute_target=aml_compute,
        source_directory=env.sources_directory_train,
        script_name=env.first_step_script_path,
        outputs=[],
        arguments=[
            "--input_dataset_name", env.input_dataset_name,
            "--waves_dataset_name", env.waves_dataset_name
        ],
        runconfig=run_config
    )

    step_list.append(first_step)

    # Build pipeline
    pipeline = Pipeline(workspace=aml_workspace, steps=step_list)
    pipeline.validate()
    logger.info(f"Built pipeline {pipeline}")

    # Publish pipeline
    published_pipeline = pipeline.publish(env.pipeline_name, description=env.pipeline_name, version=datetime.utcnow().isoformat())
    try:
        pipeline_endpoint = PipelineEndpoint.get(workspace=aml_workspace, name=env.pipeline_endpoint_name)
        pipeline_endpoint.add_default(published_pipeline)
    except ErrorResponseException:
        pipeline_endpoint = PipelineEndpoint.publish(workspace=aml_workspace, name=env.pipeline_endpoint_name, pipeline=published_pipeline, description=env.pipeline_endpoint_name)


if __name__ == "__main__":
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    logger.propagate = False
    sh = StreamHandler()
    sh.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)
    main()
