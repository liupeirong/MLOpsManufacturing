import pytest
import logging
from pytest_mock import MockFixture
from src.PipelineRunMonitor.pipeline_run_monitor import main
import azure.functions as func


def test_pipeline_run_monitor_success(monkeypatch, mocker: MockFixture):
    """ Test main function for expected success
    """
    # arrange
    monkeypatch.setenv("WORKSPACE_NAME", "mock_workspace_name")
    monkeypatch.setenv("SUBSCRIPTION_ID", "mock_subscription_id")
    monkeypatch.setenv("RESOURCE_GROUP", "mock_resource_group")
    monkeypatch.setenv("APP_INSIGHTS_CONNECTION_STRING", "InstrumentationKey=00000000-0000-0000-0000-000000000001")

    # create mock logger by assign name and info function
    mock_logger = logging.getLogger('src.PipelineRunMonitor.pipeline_run_monitor')
    mock_logger_info = mocker.patch.object(mock_logger, 'info')

    mock_workspace = mocker.patch("src.PipelineRunMonitor.pipeline_run_monitor.Workspace")
    mock_run = mocker.patch("src.PipelineRunMonitor.pipeline_run_monitor.Run")
    mock_run.return_value.get.return_value = mock_run

    event = func.EventGridEvent(
        id="xxx",
        data={"runId": "xxx"},
        topic="httpxxx",
        subject="xxx",
        event_type="Microsoft.MachineLearningServices.RunCompleted",
        event_time=0,
        data_version="xxx"
    )

    # act
    main(event)

    # assert
    mock_logger_info.assert_called_once()
    mock_workspace.assert_called_once()


def test_pipeline_run_monitor_fail(monkeypatch, mocker: MockFixture):
    """ Test main function for expected failure
    """
    # arrange
    monkeypatch.setenv("WORKSPACE_NAME", "mock_workspace_name")
    monkeypatch.setenv("SUBSCRIPTION_ID", "mock_subscription_id")
    monkeypatch.setenv("RESOURCE_GROUP", "mock_resource_group")

    mock_workspace = mocker.patch("src.PipelineRunMonitor.pipeline_run_monitor.Workspace")
    mock_workspace.get.return_value = mock_workspace
    mock_run = mocker.patch("src.PipelineRunMonitor.pipeline_run_monitor.Run")
    mock_run.get.return_value = mock_run

    event = func.EventGridEvent(
        id="xxx",
        data={"xxxx": "xxx"},
        topic="httpxxx",
        subject="xxx",
        event_type="xxx",
        event_time=0,
        data_version="xxx"
    )

    # act & assert
    with (pytest.raises(Exception)) as execinfo:
        main(event)
        assert "runStatus" in str(execinfo)
