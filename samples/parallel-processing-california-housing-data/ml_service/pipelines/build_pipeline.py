"""Build pipeline."""
from datetime import datetime
from logging import INFO, Formatter, StreamHandler, getLogger

from azureml.core import Environment, Workspace
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import (Pipeline, PipelineData, PipelineEndpoint)
from azureml.pipeline.core._restclients.aeva.models.error_response import \
    ErrorResponseException
from azureml.pipeline.steps import (ParallelRunConfig, ParallelRunStep,
                                    PythonScriptStep)
from ml_service.util.env_variables import Env
from ml_service.util.pipeline_utils import get_compute


def main():
    """Build pipeline."""
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
    environment.python.conda_dependencies = conda_dep

    run_config = RunConfiguration()
    run_config.environment = environment

    # Pipeline Data
    preparation_pipelinedata = PipelineData("preparation_pipelinedata", is_directory=True).as_dataset()
    extraction_pipelinedata = PipelineData("extraction_pipelinedata", is_directory=True)
    training_pipelinedata = PipelineData("training_pipelinedata", is_directory=True)

    # List of pipeline steps
    step_list = list()
    preparation_step = PythonScriptStep(
        name="preparation-step",
        compute_target=aml_compute,
        source_directory=env.sources_directory_train,
        script_name=env.preparation_step_script_path,
        outputs=[preparation_pipelinedata],
        arguments=[
            "--input_path", env.input_dir, 
            "--output_path", preparation_pipelinedata,
            "--datastore_name", env.blob_datastore_name
        ],
        runconfig=run_config
    )

    step_list.append(preparation_step)

    parallel_run_config = ParallelRunConfig(
        source_directory=env.sources_directory_train,
        entry_script=env.extraction_step_script_path,
        mini_batch_size=env.mini_batch_size,
        error_threshold=env.error_threshold,
        output_action="append_row",
        environment=environment,
        compute_target=aml_compute,
        node_count=env.node_count,
        run_invocation_timeout=env.run_invocation_timeout,
        process_count_per_node=env.process_count_per_node,
        append_row_file_name="extraction_output.txt")
    
    extraction_step = ParallelRunStep(
        name="extraction-step",
        inputs=[preparation_pipelinedata],
        output=extraction_pipelinedata,
        arguments=[
            "--output_dir", extraction_pipelinedata
        ],
        parallel_run_config=parallel_run_config
    )
    step_list.append(extraction_step)

    training_step = PythonScriptStep(
        name="traning-step",
        compute_target=aml_compute,
        source_directory=env.sources_directory_train,
        script_name=env.training_step_script_path,
        inputs=[extraction_pipelinedata],
        outputs=[training_pipelinedata],
        arguments=[
            "--input_dir", extraction_pipelinedata,
            "--output_dir", training_pipelinedata
        ],
        runconfig=run_config
    )

    step_list.append(training_step)

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
