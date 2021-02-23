from azureml_appinsights_logger.azureml_logger import AzureMlLogger
from azureml_appinsights_logger.logger_interface import Severity


def test_get_callee_returns_callee_file_with_line_number():
    # arrange
    logger = AzureMlLogger()
    expected = "test_azureml_logger.py:11"

    # act
    actual = logger.get_callee(0)

    # assert
    assert expected == actual


def test_get_callee_details_returns_callee_module_file_with_line_number(): # noqa E501
    # arrange
    logger = AzureMlLogger()
    expected_module = "test_azureml_logger"
    expected_file_name = "test_azureml_logger.py"
    expected_line_number = 25

    # act
    actual = logger.get_callee_details(0)

    # assert
    assert actual[0] == expected_module
    assert actual[1].split("/")[-1] == expected_file_name
    assert actual[2] == expected_line_number


def test_log_metric_calls_log(mocker):
    # arrange
    mocked_run = mocker.MagicMock()
    mocked_run.parent = mocker.MagicMock()
    logger = AzureMlLogger(mocked_run)

    # act - don't log parent
    logger.log_metric('FOO', 1, 'BAR', False)

    # assert
    mocked_run.log.assert_called_once_with('FOO', 1, 'BAR')
    mocked_run.parent.log.assert_not_called()

    # act - log parent
    logger.log_metric('FOO', 1, 'BAR', True)

    # assert
    mocked_run.log.assert_called_once_with('FOO', 1, 'BAR')
    mocked_run.parent.log.assert_called_once_with('FOO', 1, 'BAR')


def test_log_metric_logs_nothing_when_metric_name_empty(mocker):
    # arrange
    mocked_run = mocker.MagicMock()
    mocked_run.parent = mocker.MagicMock()
    logger = AzureMlLogger(mocked_run)

    # act - don't log parent
    logger.log_metric('', 1, 'BAR', False)

    # assert
    mocked_run.log.assert_not_called()
    mocked_run.parent.log.assert_not_called()

    # act - log parent
    logger.log_metric('', 1, 'BAR', True)

    # assert
    mocked_run.log.assert_not_called()
    mocked_run.parent.log.assert_not_called()


def test_log_honors_severity(mocker, capsys):
    # arrange
    mocker.patch(
        'azureml_appinsights_logger.env_variables.Env.log_to_console',
        new_callable=mocker.PropertyMock,
        return_value=False
    )
    mocker.patch(
        'azureml_appinsights_logger.env_variables.Env.log_level',
        new_callable=mocker.PropertyMock,
        return_value='WARNING'
    )
    logger = AzureMlLogger()

    # act
    logger.log('FOO', Severity.WARNING)

    # assert
    captured = capsys.readouterr()
    assert 'WARNING' in captured.out
    assert 'FOO' in captured.out

    # act - lower severity
    logger.log('FOO')
    captured = capsys.readouterr()

    # assert
    assert captured.out == ""


def test_except_sets_severity(mocker):
    # arrange
    mock_log = mocker.patch(
        'azureml_appinsights_logger.azureml_logger.AzureMlLogger.log')
    logger = AzureMlLogger()
    exception = Exception('FOO')

    # act
    logger.exception(exception)

    # assert
    mock_log.assert_called_once_with(exception, Severity.CRITICAL)


def test_log_nothing_when_log_text_to_aml_is_false(mocker, capsys):
    # arrange
    mocker.patch(
        'azureml_appinsights_logger.env_variables.Env.log_to_console',
        new_callable=mocker.PropertyMock,
        return_value=True
    )
    logger = AzureMlLogger()

    # act
    logger.log('FOO', Severity.CRITICAL)

    # assert
    captured = capsys.readouterr()
    assert captured.out == ""


def test_log_when_log_text_to_aml_is_true(mocker, capsys):
    # arrange
    mocker.patch(
        'azureml_appinsights_logger.env_variables.Env.log_to_console',
        new_callable=mocker.PropertyMock,
        return_value=False
    )
    logger = AzureMlLogger()

    # act
    logger.log('FOO', Severity.CRITICAL)

    # assert
    captured = capsys.readouterr()
    assert 'FOO' in captured.out
