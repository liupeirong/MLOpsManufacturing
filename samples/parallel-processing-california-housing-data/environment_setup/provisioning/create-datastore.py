from azureml.core import Dataset, Datastore, Workspace
from azureml.data.datapath import DataPath
from ml_service.util.env_variables import Env
from msrest.exceptions import HttpOperationError

# Environment variables
env = Env()

# Azure ML workspace
aml_workspace = Workspace.get(
    name=env.workspace_name,
    subscription_id=env.subscription_id,
    resource_group=env.resource_group,
)

# Name of the datastore to workspace
blob_datastore_name = env.blob_datastore_name
# Name of Azure blob container
container_name = env.blob_container_name
# Storage account name
account_name = env.storage_account_name
# Storage account access key
account_key = env.storage_account_key

# Verify that the blob store does not exist already
try:
    blob_datastore = Datastore.get(aml_workspace, blob_datastore_name)
    print('Found existing datastore, use it.')
except HttpOperationError:
    blob_datastore = Datastore.register_azure_blob_container(workspace=aml_workspace,
                                                             datastore_name=blob_datastore_name,
                                                             container_name=container_name,
                                                             account_name=account_name,
                                                             account_key=account_key)
    print("Registered blob datastore with name: %s" % blob_datastore_name)

