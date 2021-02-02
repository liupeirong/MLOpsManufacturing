import unittest
from unittest.mock import patch

from src.observability import Observability
from src.logger_interface import Severity


class ObservabilityMock(Observability):
    @patch("src.app_insights_logger.AppInsightsLogger")
    @patch("src.azure_ml_logger.AzureMlLogger")
    @patch("src.console_logger.ConsoleLogger")
    @patch("src.observability.Loggers")
    def __init__(self, mock_loggers, mock_console_logger, mock_aml_logger,
                 mock_app_insight_logger):
        mock_loggers.loggers = [mock_console_logger, mock_aml_logger,
                                mock_app_insight_logger]
        self._loggers = mock_loggers


class TestObservability(unittest.TestCase):
    @patch("src.observability.Observability")
    def setUp(self, mock_observability):
        self.observability = mock_observability

    def test_log_metric_called_with_parameters(self):
        self.observability.log_metric("FOO", "BAZ", "BAR")

        self.observability.log_metric.assert_called_with("FOO", "BAZ", "BAR")

    def test_log_called_with_parameters(self):
        self.observability.log("FOO", Severity.CRITICAL)

        self.observability.log.assert_called_with("FOO", Severity.CRITICAL)

    def test_log_metric_is_being_called_by_all_loggers(self):
        # Force creating a new singleton on base class
        Observability._instance = None
        self.observability = ObservabilityMock()
        self.observability.log_metric("FOO", "BAZ", "BAR")

        self.observability._loggers.loggers[0].log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False
        )
        self.observability._loggers.loggers[1].log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False
        )
        self.observability._loggers.loggers[2].log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False
        )

    def test_log_is_being_called_by_all_loggers(self):
        # Force creating a new singleton on base class
        Observability._instance = None
        self.observability = ObservabilityMock()

        self.observability.log("FOO", Severity.CRITICAL)

        self.observability._loggers.loggers[0].\
            log.assert_called_with("FOO", Severity.CRITICAL)
        self.observability._loggers.loggers[1].\
            log.assert_called_with("FOO", Severity.CRITICAL)
        self.observability._loggers.loggers[2].\
            log.assert_called_with("FOO", Severity.CRITICAL)


if __name__ == "__main__":
    unittest.main()
