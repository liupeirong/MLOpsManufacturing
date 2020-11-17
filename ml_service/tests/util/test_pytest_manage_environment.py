import pytest
from pytest_mock import MockFixture
from azureml.core import Environment
from ml_service.util.manage_environment import get_environment


@pytest.fixture
def workspace(mocker: MockFixture):
    return mocker.patch('azureml.core.Workspace')


def test_manage_environment_dockerfile_automock(mocker: MockFixture,
                                                workspace):
    """Create a new AML environment with referencing a Dockerfile

    Framework: pytest-mock (https://github.com/pytest-dev/pytest-mock/)
               pytest-mock is a wrapper for unittest.mock.patch

    Differentiator: Not using any custom mock. While slightly less
            control it is more convenient to track method calls to the cost
            that not all attributes can be asserted.

    Arguments:
        mocker (MockFixture) -- Used to mock various AML classes,
                                methods and properties
        workspace -- This is a pytest fixture,
                      holds an Azure ML Workspace object
    """
    # Mock the environment to return a already existing environment
    mock_aml_env = mocker.patch('azureml.core.Environment.list')
    mock_aml_env.return_value = {"mock_env_name": mock_aml_env}

    # Mock for instantiation of Environment mock objects
    mocker.patch('azureml.core.Environment.__new__')

    # Actual method call
    result = get_environment(
                workspace,
                'env_name',
                create_new=True,
                enable_docker=True,
                # Cannot mock open
                # with pytest_mock, referencing real file instead
                # (https://docs.python.org/3/library/unittest.mock.html#mock-open)
                dockerfile='ml_model/preprocessing/Dockerfile'
            )  #

    # Assertions
    assert result.docker.enabled is True
    # Due to nature of Environment mock does not assign name attribute
    # assert result.name == 'env_name'
    assert result.docker.base_dockerfile.\
        startswith('FROM ubuntu') is True
    assert result.python.user_managed_dependencies is True
    Environment.list.assert_called()
    result.register.assert_called()
