import logging
import uuid

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
        self.run_id = self.get_run_id(run)
        self.logger = logging.getLogger(__name__)
        self.logger.level = getattr(logging, self.env.log_level.upper(), None)

    def log_metric(
        self, name="", value="", description="", log_parent=False,
    ):
        self.logger.info(f"Logging Metric for runId={self.run_id}: "
                         "name={name} value={value} "
                         "description={description} log_parent={log_parent}")

    def log(self, description="", severity=Severity.INFO):
        """
        Sends the logs to App Insights
        :param description: log description
        :param severity: log severity
        :return:
        """

        if severity == self.severity.DEBUG:
            self.logger.debug(description)
        elif severity == self.severity.INFO:
            self.logger.info(description)
        elif severity == self.severity.WARNING:
            self.logger.warning(description)
        elif severity == self.severity.ERROR:
            self.logger.error(description)
        elif severity == self.severity.CRITICAL:
            self.logger.critical(description)

    def get_run_id(self, run):
        """
        gets the correlation ID by the in following order:
        - If the script is running  in an Online run Context of AML --> run_id
        - If the script is running where a build_id
        environment variable  is set --> build_id
        - Else --> generate a unique id
        :param run:
        :return: correlation_id
        """
        run_id = str(uuid.uuid1())
        if not run.id.startswith(self.OFFLINE_RUN):
            run_id = run.id
        elif self.env.build_id:
            run_id = self.env.build_id
        return run_id
