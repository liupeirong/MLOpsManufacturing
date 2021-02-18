import pytest
from pytest_mock import MockFixture
from azureml.exceptions import ComputeTargetException
from ml_service.util.pipeline_utils import get_compute, get_environment, find_pipeline_by_name


@pytest.fixture
def workspace(mocker: MockFixture):
    return mocker.patch('azureml.core.Workspace')


def test_get_aml_compute_already_exists(mocker: MockFixture, workspace):
    expected_compute = mocker.patch('azureml.core.compute.ComputeTarget', spec=True)
    compute_targets = mocker.PropertyMock(return_value={"compute_target": expected_compute})
    type(workspace).compute_targets = compute_targets
    compute = get_compute(workspace=workspace, compute_name="compute_target")
    assert compute == expected_compute


def test_get_aml_compute_throws_exception(mocker: MockFixture, workspace):
    compute_targets = mocker.PropertyMock(side_effect=ComputeTargetException("Error while creating compute!"))
    type(workspace).compute_targets = compute_targets
    with pytest.raises(SystemExit):
        get_compute(workspace=workspace, compute_name="compute_target")


def test_get_aml_environment(mocker: MockFixture, workspace):
    mock_aml_env = mocker.patch('azureml.core.Environment.list')
    mock_aml_env.return_value = {"mock_env_name": mock_aml_env}

    aml_environment = get_environment(workspace=workspace,
                                      environment_name="mock_env_name",
                                      conda_dependencies_file="",
                                      create_new=False,
                                      enable_docker=None,
                                      use_gpu=False
                                      )
    assert aml_environment


def test_get_aml_conda_environment(mocker: MockFixture, workspace):
    mock_aml_env = mocker.patch('azureml.core.Environment.list')
    mock_aml_env.return_value = {}

    mocker.patch('azureml.core.Environment.from_conda_specification')

    aml_environment = get_environment(workspace=workspace,
                                      environment_name="mock_env_name",
                                      conda_dependencies_file="mock_conda_env_name",
                                      create_new=False,
                                      enable_docker=None,
                                      use_gpu=False
                                      )
    assert aml_environment


def test_get_aml_conda_docker_environment(mocker: MockFixture, workspace):
    mock_aml_env = mocker.patch('azureml.core.Environment.list')
    mock_aml_env.return_value = {}

    mocker.patch('azureml.core.Environment.from_conda_specification')

    aml_environment = get_environment(workspace=workspace,
                                      environment_name="mock_env_name",
                                      conda_dependencies_file="mock_conda_env_name",
                                      create_new=False,
                                      enable_docker=True,
                                      use_gpu=False
                                      )
    assert aml_environment


def test_get_aml_environment_exception_if_environment_unexists(mocker: MockFixture, workspace):
    mock_aml_env = mocker.patch('azureml.core.Environment.list')
    mock_aml_env.return_value = {}

    with pytest.raises(SystemExit):
        get_environment(workspace=workspace,
                        environment_name="mock_env_name",
                        conda_dependencies_file="mock_conda_env_name",
                        create_new=False,
                        enable_docker=None,
                        use_gpu=False
                        )


def test_find_pipeline_by_name(mocker: MockFixture, workspace):
    mock_aml_pipelines = mocker.patch('azureml.pipeline.core.PublishedPipeline.list')
    mock_aml_pipeline = mocker.patch('azureml.pipeline.core.PublishedPipeline')
    name = mocker.PropertyMock(return_value="mock_pipeline_name")
    version = mocker.PropertyMock(return_value="2020-01-12T14:12:06.000")
    type(mock_aml_pipeline).name = name
    type(mock_aml_pipeline).version = version
    mock_aml_pipelines.return_value = {mock_aml_pipeline}

    matched_pipelines = find_pipeline_by_name(aml_workspace=workspace,
                                              pipeline_name="mock_pipeline_name"
                                              )
    assert matched_pipelines


def test_find_pipeline_by_name_return_none_if_pipeline_unexists(mocker: MockFixture, workspace):
    mock_aml_pipelines = mocker.patch('azureml.pipeline.core.PublishedPipeline.list')
    mock_aml_pipeline = mocker.patch('azureml.pipeline.core.PublishedPipeline')
    name = mocker.PropertyMock(return_value="mock_pipeline_A")
    version = mocker.PropertyMock(return_value="2020-01-12T14:12:06.000")
    type(mock_aml_pipeline).name = name
    type(mock_aml_pipeline).version = version
    mock_aml_pipelines.return_value = {mock_aml_pipeline}

    matched_pipelines = find_pipeline_by_name(aml_workspace=workspace,
                                              pipeline_name="unexist_mock_pipeline"
                                              )

    assert matched_pipelines is None
