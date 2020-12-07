
import os
from azureml.core import Workspace, Environment
from ml_service.util.env_variables import Env
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, DEFAULT_GPU_IMAGE
from ml_service.util.logger.observability import observability


def get_environment(
    workspace: Workspace,
    environment_name: str,
    conda_dependencies_file: str = None,
    create_new: bool = False,
    enable_docker: bool = None,
    docker_image: str = None,
    dockerfile: str = None,
    use_gpu: bool = False,
):
    try:
        e = Env()
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:

            # Environment has to be created
            if conda_dependencies_file is not None:
                new_env = Environment.from_conda_specification(
                    environment_name,
                    os.path.join(e.sources_directory_train, conda_dependencies_file),  # NOQA: E501
                )  # NOQA: E501
                restored_environment = new_env
            else:
                restored_environment = Environment(environment_name)

            if enable_docker is not None:
                restored_environment.docker.enabled = enable_docker

                if docker_image is not None:
                    restored_environment.docker.base_image = docker_image
                    # In case of own image
                    # don't append AML managed dependencies
                    restored_environment.python.\
                        user_managed_dependencies = True
                elif dockerfile is not None:
                    # Alternatively, load from a file.
                    with open(dockerfile, "r") as f:
                        dockerfile = f.read()
                        restored_environment.docker.\
                            base_dockerfile = dockerfile
                    # In case of own Dockerfile
                    # don't append AML managed dependencies
                    restored_environment.python.\
                        user_managed_dependencies = True
                else:
                    restored_environment.docker.\
                        base_image = DEFAULT_GPU_IMAGE if use_gpu else DEFAULT_CPU_IMAGE  # NOQA: E501

            restored_environment.register(workspace)

        if restored_environment is not None:
            observability.log(restored_environment)
        return restored_environment
    except Exception as e:
        observability.exception(e)
        exit(1)
