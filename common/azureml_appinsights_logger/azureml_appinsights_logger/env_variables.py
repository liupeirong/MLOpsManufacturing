from dataclasses import dataclass, field
from typing import Optional
import os
from dotenv import load_dotenv, find_dotenv


@dataclass(frozen=True)
class Env:
    """Loads all environment variables into a predefined set of properties
    """

    dotenv_path = find_dotenv()
    print(f"find_dotenv returns: {dotenv_path}")
    load_dotenv(dotenv_path)

    app_insights_connection_string: Optional[str] = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")  # NOQA: E501
    log_to_console: Optional[bool] = os.environ.get("LOG_TO_CONSOLE", "true").lower().strip() == "true"  # NOQA: E501
    log_text_to_aml: bool = field(init=False)
    log_level: Optional[str] = os.environ.get("LOG_LEVEL", "WARNING")  # NOQA: E501
    log_sampling_rate: float = float(os.environ.get("LOG_SAMPLING_RATE", 1.0))  # NOQA: E501
    trace_sampling_rate: float = float(os.environ.get("TRACE_SAMPLING_RATE", 1.0))  # NOQA: E501
    metrics_export_interval: int = int(os.environ.get("METRICS_EXPORT_INTERVAL", 15))  # NOQA: E501
    enable_standard_metrics: Optional[bool] = os.environ.get("ENABLE_STANDARD_METRICS", "false").lower().strip() == "true"  # NOQA: E501

    build_id: Optional[str] = str(os.environ.get("BUILD_ID", "local"))  # NOQA: E501

    def __post_init__(self):
        # aml and console both print messages
        object.__setattr__(self, 'log_text_to_aml', not self.log_to_console)
