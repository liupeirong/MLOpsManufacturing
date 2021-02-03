import unittest
from unittest.mock import patch

from src.console_logger import ConsoleLogger


class MockRun:
    def __init__(self, run_id):
        self.id = run_id
        self.name = run_id


class TestObservability(unittest.TestCase):
    @patch.object(ConsoleLogger, "log")
    def test_log_metric_called_with_parameters(self, mock_log):
        run = MockRun("OfflineRun")
        logger = ConsoleLogger(run)
        logger.log_metric("FOO", "BAZ", "BAR", False)
        mock_log.assert_called_with(
            "Logging Metric for runId=local: name=FOO value=BAZ"
            " description=BAR log_parent=False")


if __name__ == "__main__":
    unittest.main()
