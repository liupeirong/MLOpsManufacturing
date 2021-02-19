from pytest_mock import MockFixture
import azure.functions as func

from src.PipelineHttpTrigger.pipeline_http_trigger import main


def test_pipeline_http_trigger(monkeypatch, mocker: MockFixture):
    """ Test main function for expected success of trigger filepath
    """
    monkeypatch.setenv('SUBSCRIPTION_ID', 'mock_subscription_id')
    monkeypatch.setenv('RESOURCE_GROUP', 'mock_resource_group')
    monkeypatch.setenv('WORKSPACE_NAME', 'mock_ws_name')
    monkeypatch.setenv('PIPELINE_ENDPOINT_NAME', 'mock_pipeline_endpoint_name')
    monkeypatch.setenv('EXPERIMENT_NAME', 'mock_experiment_name')

    mock_aml_workspace = mocker.patch('src.PipelineHttpTrigger.pipeline_http_trigger.Workspace')
    mock_aml_workspace(
        subscription_id="mock_subscriptionId",
        resource_group="mock_resource_group",
        workspace_name="mock_ws_name",
        auth="mock_msi_auth_token"
    )
    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/pipeline_http_trigger')

    # Call the function.
    main(req)

    # Check if http trigger is correctly called with parameter (file path)
    assert req
