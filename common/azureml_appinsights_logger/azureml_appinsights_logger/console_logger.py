import logging

from .env_variables import Env
from .logger_interface import (
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
        msg = f"Logging Metric for runId={self.run_id}: " \
            f"name={name} value={value} description={description} " \
            f"log_parent={log_parent}"
        print(msg)

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
