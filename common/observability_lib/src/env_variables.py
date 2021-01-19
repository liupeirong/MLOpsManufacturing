from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    """Loads all environment variables into a predefined set of properties
    """

    # to load .env file into environment variables for local execution
    load_dotenv()

    # variables from Azure DevOps variable group
    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")
    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")

    app_insights_connection_string: Optional[str] = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")  # NOQA: E501
    log_to_console: Optional[bool] = os.environ.get("LOG_TO_CONSOLE", "false").lower().strip() == "true"  # NOQA: E501
    log_level: Optional[str] = os.environ.get("LOG_LEVEL", "WARNING")  # NOQA: E501
    log_sampling_rate: float = float(os.environ.get("LOG_SAMPLING_RATE", 1.0))  # NOQA: E501
    trace_sampling_rate: float = float(os.environ.get("TRACE_SAMPLING_RATE", 1.0))  # NOQA: E501
    metrics_export_interval: int = int(os.environ.get("METRICS_EXPORT_INTERVAL", 15))  # NOQA: E501
