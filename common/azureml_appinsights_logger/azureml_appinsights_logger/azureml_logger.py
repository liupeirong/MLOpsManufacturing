import logging
import datetime
import time

from .env_variables import Env
from .logger_interface import (
    LoggerInterface,
    ObservabilityAbstract,
    Severity,
)


class AzureMlLogger(LoggerInterface, ObservabilityAbstract):
    def __init__(self, run=None):
        self.env = Env()
        self.level = getattr(logging, self.env.log_level.upper(), "WARNING")
        self.run = run

    def log_metric(self, name, value, description, log_parent):
        """Log a metric value to the run with the given name.
        :param log_parent: mark True  if you want to log to parent Run
        :param name: The name of metric.
        :type name: str
        :param value: The value to be posted to the service.
        :type value:
        :param description: An optional metric description.
        :type description: str
        """
        if name != "":
            self.run.log(
                name, value, description
            ) if log_parent is False or self.run.parent is None \
                else self.run.parent.log(name, value, description)

    def log(self, description="", severity=Severity.INFO):
        """
        Sends the logs to AML (experiments -> logs/outputs)
        :param description: log description
        :param severity: log severity
        :return:
        """
        if self.level <= severity and self.env.log_text_to_aml:
            time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            callee = self.get_callee(
                2
            )  # to get the script who is calling Observability
            print(
                "{}, [{}], {}:{}".format(
                    time_stamp, self.severity_map[severity],
                    callee, description
                )
            )

    def exception(self, exception: Exception):
        """
        Prints the exception to console
        :param exception: Actual exception to be sent
        :return:
        """
        self.log(exception, Severity.CRITICAL)
