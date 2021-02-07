import pytest
from src.console_logger import ConsoleLogger
from src.logger_interface import Severity


@pytest.fixture(name="mock_run")
def mock_run(mocker):
    mocker.patch(
        'src.logger_interface.ObservabilityAbstract.get_run_id_and_set_context',  # noqa #501
        return_value="MYRUN")
    return mocker.patch('azureml.core.Run')


def test_log_metric(mocker, mock_run):
    # arrange:
    logger = ConsoleLogger(mock_run)
    spy = mocker.spy(logger, 'log')

    # act:
    logger.log_metric("FOO", "BAZ", "BAR", False)

    # assert:
    spy.assert_called_once_with(
        "Logging Metric for runId=MYRUN: name=FOO value=BAZ"
        " description=BAR log_parent=False")


def test_dont_log_when_severity_lower(mocker, mock_run, capsys):
    # arrange:
    logger = ConsoleLogger(mock_run)
    logger.level = Severity.WARNING
    logger.custom_dimensions = 'BAR'

    # act:
    logger.log("FOO", Severity.INFO)

    # assert:
    captured = capsys.readouterr()
    assert captured.out == ""


def test_log_when_severity_higher(mocker, mock_run, capsys):
    # arrange:
    logger = ConsoleLogger(mock_run)
    logger.level = Severity.WARNING
    logger.custom_dimensions = 'BAR'

    # act:
    logger.log("FOO", Severity.WARNING)

    # assert:
    captured = capsys.readouterr()
    assert captured.out == "FOO - custom dimensions: BAR\n"


def test_log_with_default_severity(mocker, mock_run, capsys):
    # arrange:
    mocker.patch.object(ConsoleLogger.log, "__defaults__", (Severity.WARNING,))
    logger = ConsoleLogger(mock_run)
    logger.level = Severity.INFO
    logger.custom_dimensions = 'BAR'
    spy = mocker.spy(logger, 'log')

    # act:
    logger.log("FOO")

    # assert:
    spy.assert_called_once_with("FOO")
    captured = capsys.readouterr()
    assert captured.out == "FOO - custom dimensions: BAR\n"
