import logging

from ml_service.util.env_variables import Env
from ml_service.util.logger.logger_interface import (
    LoggerInterface,
    ObservabilityAbstract,
    Severity,
)


class ConsoleLogger(LoggerInterface, ObservabilityAbstract):
    def __init__(self, run):
        self.env = Env()
        # initializes log exporter
        self.run_id = self.get_run_id_and_set_context(run)
        self.level = getattr(logging, self.env.log_level.upper(), "WARNING")

    def log_metric(
        self, name="", value="", description="", log_parent=False,
    ):
        self.log(f"Logging Metric for runId={self.run_id}: "
                 "name={name} value={value} "
                 "description={description} log_parent={log_parent}")

    def log(self, description="", severity=Severity.INFO):
        """
        Prints the logs to console
        :param description: log description
        :param severity: log severity
        :return:
        """
        if self.level <= severity:
            print(f"{description} - custom dimensions:"
                  f" {self.custom_dimensions}")

    def exception(self, exception: Exception):
        """
        Prints the exception to console
        :param exception: Actual exception to be sent
        :return:
        """
        print(exception)
