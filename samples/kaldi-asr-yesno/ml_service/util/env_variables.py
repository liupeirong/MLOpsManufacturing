"""Env dataclass to load and hold all environment variables
"""
from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    """Loads all environment variables into a predefined set of properties
    """

    # to load .env file into environment variables for local execution
    load_dotenv()

    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")

    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")
    aml_env_name: Optional[str] = os.environ.get("AML_ENV_NAME")
    compute_name: Optional[str] = os.environ.get("AML_COMPUTE_CLUSTER_NAME")

    blob_datastore_name: Optional[str] = os.environ.get("AML_BLOB_DATASTORE_NAME")
    storage_account_name: Optional[str] = os.environ.get("AML_STORAGE_ACCOUNT_NAME")
    blob_container_name: Optional[str] = os.environ.get("AML_BLOB_CONTAINER_NAME")
    storage_account_key: Optional[str] = os.environ.get("AML_STORAGE_ACCOUNT_KEY")

    pipeline_endpoint_name: Optional[str] = os.environ.get("PIPELINE_ENDPOINT_NAME")
    pipeline_name: Optional[str] = os.environ.get("PIPELINE_NAME")

    input_dataset_name: Optional[str] = os.environ.get("AML_INPUT_DATASET_NAME")
    waves_dataset_name: Optional[str] = os.environ.get("AML_WAVES_DATASET_NAME")

    sources_directory_train: Optional[str] = os.environ.get("SOURCES_DIR_TRAIN")
    first_step_script_path: Optional[str] = os.environ.get("FIRST_STEP_SCRIPT_PATH")

    acr_image: Optional[str] = os.environ.get("ACR_IMAGE")
    acr_address: Optional[str] = os.environ.get("ACR_ADDRESS")
    acr_username: Optional[str] = os.environ.get("ACR_USERNAME")
    acr_password: Optional[str] = os.environ.get("ACR_PASSWORD")
