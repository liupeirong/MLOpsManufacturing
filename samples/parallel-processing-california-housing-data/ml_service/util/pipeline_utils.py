from datetime import datetime as dt
from typing import Union

import numpy as np
from azureml.core import Environment, Workspace
from azureml.core.environment import DEFAULT_CPU_IMAGE, DEFAULT_GPU_IMAGE
from azureml.exceptions import ComputeTargetException
from azureml.pipeline.core import PublishedPipeline


def get_compute(workspace: Workspace, compute_name: str):
    try:
        if compute_name in workspace.compute_targets:
            compute_target = workspace.compute_targets[compute_name]
        return compute_target
    except ComputeTargetException as ex:
        print(ex)
        print("An error occurred trying to provision compute.")
        exit(1)


def get_environment(
    workspace: Workspace,
    environment_name: str,
    conda_dependencies_file: str,
    create_new: bool = False,
    enable_docker: bool = None,
    use_gpu: bool = False
):
    try:
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:
            new_env = Environment.from_conda_specification(
                environment_name,
                conda_dependencies_file,
            )
            restored_environment = new_env
            if enable_docker is not None:
                restored_environment.docker.enabled = enable_docker
                restored_environment.docker.base_image = DEFAULT_GPU_IMAGE if use_gpu else DEFAULT_CPU_IMAGE
            restored_environment.register(workspace)

        if restored_environment is not None:
            print(restored_environment)
        return restored_environment
    except Exception as e:
        print(e)
        exit(1)


def find_pipeline_by_name(aml_workspace: Workspace, pipeline_name: str) -> Union[PublishedPipeline, None]:
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipelines = list(filter(lambda p: p.name == pipeline_name, pipelines))
    date_matched_pipelines = [dt.strptime(pipeline.version, "%Y-%m-%dT%H:%M:%S.%f") for pipeline in matched_pipelines]
    matched_pipelines = [matched_pipelines[idx] for idx in np.argsort(date_matched_pipelines)]

    if matched_pipelines:
        return matched_pipelines[-1]
    return None
