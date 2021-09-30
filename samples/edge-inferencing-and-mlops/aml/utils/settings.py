import os
from dotenv import load_dotenv

load_dotenv()

# Load Azure variables
subscription_id = os.getenv('SUBSCRIPTION_ID')
workspace_resource_group = os.getenv('WORKSPACE_RESOURCE_GROUP')
datastore_resource_group = os.getenv('DATASTORE_RESOURCE_GROUP')
tenant_id = os.getenv('AAD_TENANT_ID')
app_id = os.getenv('AAD_SERVICE_PRINCIPAL_ID')
app_secret = os.getenv('AAD_SERVICE_PRINCIPAL_SECRET')

# Load Azure ML variables
workspace_name = os.getenv('WORKSPACE_NAME')
compute_target_name = os.getenv('COMPUTE_TARGET_NAME')
aml_pipeline_name = os.getenv('AML_PIPELINE_NAME')
datastore_name = os.getenv('DATASTORE_NAME')
datastore_container_name = os.getenv('DATASTORE_CONTAINER_NAME')
environment_name = os.getenv('ENVIRONMENT_NAME')
environment_version = os.getenv('ENVIRONMENT_VERSION')
environment_base_image = os.getenv('ENVIRONMENT_BASE_IMAGE')
experiment_name = os.getenv('EXPERIMENT_NAME')
data_storage_account_name = os.getenv('DATA_STORAGE_ACCOUNT_NAME')
data_storage_account_key = os.getenv('DATA_STORAGE_ACCOUNT_KEY')

# Load training variables
model_name = os.getenv('MODEL_NAME')
build_id = os.getenv('BUILD_ID')
build_source = os.getenv('BUILD_SOURCE')
