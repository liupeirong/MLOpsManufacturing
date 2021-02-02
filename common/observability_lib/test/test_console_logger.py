import unittest
from unittest.mock import patch

from src.console_logger import ConsoleLogger


class TestObservability(unittest.TestCase):
    @patch("src.console_logger.ConsoleLogger")
    def setUp(self, mock_console_logger):
        self.console_logger = mock_console_logger

    def test_log_called_with_parameters(self):
        self.console_logger.log("FOO", "BAZ")

        self.console_logger.log.assert_called_with("FOO", "BAZ")

    def test_log_metric_called_with_parameters(self):
        self.console_logger.log_metric("FOO", "BAZ", "BAR", False)

        self.console_logger.log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False)


if __name__ == "__main__":
    unittest.main()
