import pytest
from azureml_appinsights_logger.observability import Observability
from azureml_appinsights_logger.logger_interface import Severity


@pytest.fixture
def mock_loggers(mocker):
    mock_loggers = mocker.patch(
        "azureml_appinsights_logger.observability.Loggers")
    mock_appinsights_logger = mocker.patch(
        "azureml_appinsights_logger.appinsights_logger.AppInsightsLogger")
    mock_aml_logger = mocker.patch(
        "azureml_appinsights_logger.console_logger.ConsoleLogger")
    mock_console_logger = mocker.patch(
        "azureml_appinsights_logger.azureml_logger.AzureMlLogger")
    mock_loggers.loggers = [
        mock_appinsights_logger,
        mock_aml_logger,
        mock_console_logger]
    return mock_loggers


def test_log_metric_is_called_by_all_loggers(mocker, mock_loggers):
    # arrange
    mocker.patch(
        'azureml_appinsights_logger.observability.Observability._loggers',
        new_callable=mocker.PropertyMock,
        return_value=mock_loggers,
        create=True
    )

    # act
    mock_observability = Observability()
    mock_observability.log_metric("FOO", "BAZ", "BAR")

    # assert
    mock_observability._loggers.loggers[0].log_metric.assert_called_with(
        "FOO", "BAZ", "BAR", False)
    mock_observability._loggers.loggers[1].log_metric.assert_called_with(
        "FOO", "BAZ", "BAR", False)
    mock_observability._loggers.loggers[2].log_metric.assert_called_with(
        "FOO", "BAZ", "BAR", False)


def test_log_is_called_by_all_loggers(mocker, mock_loggers):
    # arrange
    mocker.patch(
        'azureml_appinsights_logger.observability.Observability._loggers',
        new_callable=mocker.PropertyMock,
        return_value=mock_loggers,
        create=True
    )

    # act
    mock_observability = Observability()
    mock_observability.log("FOO", Severity.CRITICAL)

    # assert
    mock_observability._loggers.loggers[0].log.assert_called_with(
        "FOO", Severity.CRITICAL)
    mock_observability._loggers.loggers[1].log.assert_called_with(
        "FOO", Severity.CRITICAL)
    mock_observability._loggers.loggers[2].log.assert_called_with(
        "FOO", Severity.CRITICAL)
