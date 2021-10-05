from azureml.core import Datastore, Workspace
from azureml.core.runconfig import RunConfiguration
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.exceptions import WorkspaceException
from msrest.exceptions import AuthenticationError, HttpOperationError
from utils.environment import get_environment


def get_workspace(
        name: str,
        resource_group: str,
        subscription_id: str,
        tenant_id: str,
        app_id: str,
        app_secret: str):

    if not name:
        raise ValueError("name is null")

    if not resource_group:
        raise ValueError("resource_group is null")

    if not subscription_id:
        raise ValueError("subscription_id is null")

    if not tenant_id:
        raise ValueError("tenant_id is null")

    if not app_id:
        raise ValueError("app_id is null")

    if not app_secret:
        raise ValueError("app_secret is null")

    service_principal = ServicePrincipalAuthentication(
        tenant_id=tenant_id,
        service_principal_id=app_id,
        service_principal_password=app_secret)

    try:
        workspace = Workspace.get(
            name=name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            auth=service_principal)

        return workspace
    except (WorkspaceException, AuthenticationError) as ex:
        print("Error while retrieving Workspace...")
        print(str(ex))
        raise


def get_workspace_configs(
        name: str,
        workspace_resource_group: str,
        datastore_resource_group: str,
        subscription_id: str,
        tenant_id: str,
        app_id: str,
        app_secret: str,
        compute_target_name: str,
        datastore_name: str,
        datastore_container_name: str,
        data_storage_account_name: str,
        data_storage_account_key: str,
        environment_name: str,
        environment_version: str,
        environment_base_image: str,
        environment_pip_requirements_path: str
):
    # Get workspace
    workspace = get_workspace(name, workspace_resource_group, subscription_id, tenant_id, app_id, app_secret)

    if not compute_target_name:
        raise ValueError("compute_target_name is null")

    if not datastore_name:
        raise ValueError("datastore_name is null")

    if not environment_pip_requirements_path:
        raise ValueError("environment_pip_requirements_path is null")

    # Get compute target
    compute_target = workspace.compute_targets[compute_target_name]

    try:
        datastore = Datastore.get(workspace, datastore_name)
    except HttpOperationError:
        print("Datastore doesn't exist")
        datastore = Datastore.register_azure_blob_container(
            workspace=workspace,
            datastore_name=datastore_name,
            account_name=data_storage_account_name,
            container_name=datastore_container_name,
            account_key=data_storage_account_key,
            subscription_id=subscription_id,
            resource_group=datastore_resource_group)

    # Get environment
    environment = get_environment(
        workspace=workspace,
        name=environment_name,
        pip_requirements_path=environment_pip_requirements_path,
        version=environment_version,
        base_image=environment_base_image
    )

    # Get run config
    run_config = RunConfiguration()
    run_config.target = compute_target
    run_config.environment = environment

    return workspace, compute_target, datastore, run_config
