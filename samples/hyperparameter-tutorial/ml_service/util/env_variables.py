import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# See /.env file
@dataclass(frozen=True)
class Env:
    load_dotenv()

    subscription_id: Optional[str] = os.getenv("SUBSCRIPTION_ID")
    resource_group: Optional[str] = os.getenv("RESOURCE_GROUP")

    aml_workspace_name: Optional[str] = os.getenv("AML_WORKSPACE_NAME")
    aml_workspace_location: Optional[str] = os.getenv("AML_WORKSPACE_LOCATION")

    aml_experiment_name: Optional[str] = os.getenv("AML_EXPERIMENT_NAME")
    aml_environment_name: Optional[str] = os.getenv("AML_ENVIRONMENT_NAME")
    aml_compute_name: Optional[str] = os.getenv("AML_COMPUTE_NAME")

    aml_model_name: Optional[str] = os.getenv("AML_MODEL_NAME")

    aml_pipeline_name: Optional[str] = os.getenv("AML_PIPELINE_NAME")
    aml_pipeline_endpoint_name: Optional[str] = os.getenv("AML_PIPELINE_ENDPOINT_NAME")
