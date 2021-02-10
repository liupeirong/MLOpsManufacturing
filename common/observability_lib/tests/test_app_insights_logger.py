from src.app_insights_logger import AppInsightsLogger, logging
import uuid
from opencensus.trace.span import SpanKind


def test_get_run_id_should_use_runid_in_online_run(mocker):
    mock_run = mocker.MagicMock()
    mock_run.id = 'FOO'
    mock_run.name = 'FOO1'
    mock_run.experiment.name = 'BAR'
    mock_run.parent.id = 'BAZ'
    mock_run.parent.get_portal_url.return_value = 'portal_url'

    expected_run_id = "FOO"
    expected_custom_dimensions = {
        'custom_dimensions': {
            "parent_run_id": 'BAZ',
            "step_id": 'FOO',
            "step_name": 'FOO1',
            "experiment_name": 'BAR',
            "run_url": 'portal_url',
            "offline_run": False
        }
    }

    # action
    logger = AppInsightsLogger(mock_run)
    actual_run_id = logger.run_id
    actual_custom_dimensions = logger.custom_dimensions

    # logger.custom_dimensions
    assert actual_run_id == expected_run_id
    assert actual_custom_dimensions == expected_custom_dimensions


def test_get_run_id_should_use_buildid_in_offline_run(mocker):
    # arrange
    mock_run = mocker.MagicMock()
    mock_run.id = 'OfflineRun'
    expected_run_id = "BAR"
    mocker.patch(
        'src.app_insights_logger.Env.build_id',
        new_callable=mocker.PropertyMock,
        return_value=expected_run_id
    )

    expected_custom_dimensions = {
        'custom_dimensions': {
            "run_id": expected_run_id,
            "offline_run": True
        }
    }

    # action
    logger = AppInsightsLogger(mock_run)
    actual_run_id = logger.run_id
    actual_custom_dimensions = logger.custom_dimensions

    # logger.custom_dimensions
    assert actual_run_id == expected_run_id
    assert actual_custom_dimensions == expected_custom_dimensions


def test_get_run_id_should_use_uuid_in_offline_run_when_no_buildid(mocker):
    # arrange
    mock_run = mocker.MagicMock()
    mock_run.id = 'OfflineRun'
    expected_run_id = "BAR"
    mocker.patch(
        'src.app_insights_logger.Env.build_id',
        new_callable=mocker.PropertyMock,
        return_value=None
    )
    mocker.patch.object(uuid, 'uuid1', return_value=expected_run_id)

    expected_custom_dimensions = {
        'custom_dimensions': {
            "run_id": expected_run_id,
            "offline_run": True
        }
    }

    # action
    logger = AppInsightsLogger(mock_run)
    actual_run_id = logger.run_id
    actual_custom_dimensions = logger.custom_dimensions

    # logger.custom_dimensions
    assert actual_run_id == expected_run_id
    assert actual_custom_dimensions == expected_custom_dimensions


def test_opencensus_init_with_env_vars(mocker):
    # arrange
    mock_run = mocker.MagicMock()
    mock_run.id = 'OfflineRun'
    mock_exporter = mocker.patch(
        'src.app_insights_logger.AzureExporter', autospec=True)
    expected_connection_string = 'FOO'
    mock_sampler = mocker.patch(
        'src.app_insights_logger.ProbabilitySampler', autospec=True)
    expected_sampling_rate = 0.7
    mock_logger = mocker.patch.object(logging, 'getLogger')
    mock_setLevel = mock_logger.return_value.setLevel
    expected_log_level_string = 'ERROR'
    expected_log_level = getattr(logging, expected_log_level_string)

    mocker.patch('src.app_insights_logger.AzureLogHandler', autospec=True)
    mocker.patch('src.app_insights_logger.metrics_exporter', autospec=True)
    mocker.patch(
        'src.app_insights_logger.Env.app_insights_connection_string',
        new_callable=mocker.PropertyMock,
        return_value=expected_connection_string
    )
    mocker.patch(
        'src.app_insights_logger.Env.trace_sampling_rate',
        new_callable=mocker.PropertyMock,
        return_value=expected_sampling_rate
    )
    mocker.patch(
        'src.app_insights_logger.Env.log_level',
        new_callable=mocker.PropertyMock,
        return_value=expected_log_level_string
    )

    # act
    AppInsightsLogger(mock_run)

    # assert
    mock_exporter.assert_called_once_with(
        connection_string=expected_connection_string)
    mock_sampler.assert_called_once_with(
        expected_sampling_rate)
    mock_setLevel.assert_called_once_with(
        expected_log_level)


def test_start_span(mocker):
    # arrange
    mock_tracer = mocker.patch(
        'src.app_insights_logger.Tracer', autospec=True)
    mock_run = mocker.MagicMock()
    mock_run.id = 'OfflineRun'
    span_name = 'FOO'

    # act
    logger = AppInsightsLogger(mock_run)
    span = logger.start_span(span_name)

    # assert
    mock_tracer.return_value.start_span.assert_called_once_with(span_name)
    assert span.span_kind == SpanKind.SERVER
    span.attributes.__setitem__.assert_any_call('http.route', span_name)
    span.attributes.__setitem__.assert_any_call('http.method', 'START')
