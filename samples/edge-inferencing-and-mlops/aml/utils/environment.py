from azureml.core import Environment, Workspace


def get_environment(
    workspace: Workspace,
    name: str,
    pip_requirements_path: str,
    version: str = None,
    base_image: str = None
):
    if workspace is None:
        raise ValueError("workspace is null")

    if not name:
        raise ValueError("environment name is null")

    if not pip_requirements_path:
        raise ValueError("Pip requirements path name is null")

    environment = None

    try:
        # Find environment
        environment = Environment.get(workspace=workspace, name=name, version=version)
    except (Exception):
        environment = Environment.from_pip_requirements(name=name, file_path=pip_requirements_path)

        if version:
            environment.version = version

        if base_image:
            environment.docker.enabled = True
            environment.docker.base_image = base_image

        environment.register(workspace=workspace)

    return environment
