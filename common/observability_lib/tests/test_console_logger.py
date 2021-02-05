from src.console_logger import ConsoleLogger


def test_log_metric(mocker):
    mocker.patch(
        'src.logger_interface.ObservabilityAbstract.get_run_id_and_set_context',  # noqa #501
        return_value="MYRUN")
    mock_log = mocker.patch('src.console_logger.ConsoleLogger.log')
    mock_run = mocker.patch('azureml.core.Run')
    logger = ConsoleLogger(mock_run)
    logger.log_metric("FOO", "BAZ", "BAR", False)
    mock_log.assert_called_with(
        "Logging Metric for runId=MYRUN: name=FOO value=BAZ"
        " description=BAR log_parent=False")
