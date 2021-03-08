"""Env dataclass to load and hold all environment variables
"""
import os
from dataclasses import dataclass
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
    compute_vm_size: Optional[str] = os.environ.get("AML_COMPUTE_VM_SIZE")
    compute_idle_time: Optional[str] = os.environ.get("AML_COMPUTE_IDLE_TIME")
    compute_min_nodes: Optional[str] = os.environ.get("AML_COMPUTE_MIN_NODES")
    compute_max_nodes: Optional[str] = os.environ.get("AML_COMPUTE_MAX_NODES")

    blob_datastore_name: Optional[str] = os.environ.get("AML_BLOB_DATASTORE_NAME")
    storage_account_name: Optional[str] = os.environ.get("AML_STORAGE_ACCOUNT_NAME")
    blob_container_name: Optional[str] = os.environ.get("AML_BLOB_CONTAINER_NAME")
    storage_account_key: Optional[str] = os.environ.get("AML_STORAGE_ACCOUNT_KEY")

    pipeline_endpoint_name: Optional[str] = os.environ.get("PIPELINE_ENDPOINT_NAME")
    pipeline_name: Optional[str] = os.environ.get("PIPELINE_NAME")

    input_dir: Optional[str] = os.environ.get("INPUT_DIR")

    mini_batch_size: Optional[str] = os.environ.get("MINI_BATCH_SIZE")
    error_threshold: Optional[int] = int(os.environ.get("ERROR_THRESHOLD"))
    node_count: Optional[int] = int(os.environ.get("NODE_COUNT"))
    process_count_per_node: Optional[int] = int(os.environ.get("PROCESS_COUNT_PER_NODE"))
    run_invocation_timeout: Optional[int] = int(os.environ.get("RUN_INVOCATION_TIMEOUT"))

    sources_directory_train: Optional[str] = os.environ.get("SOURCES_DIR_TRAIN")
    preparation_step_script_path: Optional[str] = os.environ.get("PREPARATION_STEP_SCRIPT_PATH")
    extraction_step_script_path: Optional[str] = os.environ.get("EXTRACTION_STEP_SCRIPT_PATH")
    training_step_script_path: Optional[str] = os.environ.get("TRAINING_STEP_SCRIPT_PATH")
