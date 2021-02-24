import pytest
import runpy
from pytest_mock import MockFixture
from unittest.mock import ANY
from ml_service.tests.pipelines.test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks  # NOQA: F401, E501
from ml_service.util.env_variables import Env
from azureml.pipeline.core import Pipeline
from azureml.pipeline.steps import PythonScriptStep
from collections import namedtuple


def test_build_data_processing_os_cmd_pipeline_happy_path(mocker: MockFixture,
                                                          aml_pipeline_mocks):  # NOQA: F811, E501
    """ Test Processing Pipeline build
        happy path
    """
    # Load mocks from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks

    # Create Spies
    spy_pythonscriptstep_create =\
        mocker.patch('azureml.pipeline.steps.PythonScriptStep',
                     wraps=PythonScriptStep)
    spy_pipeline_create = mocker.patch('azureml.pipeline.core.Pipeline',
                                       wraps=Pipeline)

    # run as module (start from if __name__ == "__main__")
    runpy.run_module('ml_service.pipelines.'
                     'build_data_processing_os_cmd_pipeline',
                     run_name='__main__')

    # Assertions

    # Load Mocked environment variables
    e = Env()
    # Check if the correct workspace retrieved
    mock_workspace_get.assert_called_with(name=e.workspace_name,
                                          resource_group=e.resource_group,
                                          subscription_id=e.subscription_id)

    # Check if PythonScriptStep instantiation was called correctly
    spy_pythonscriptstep_create.\
        assert_called_once_with(allow_reuse=False,
                                runconfig=ANY,
                                arguments=ANY,
                                source_directory=e.sources_directory_train,
                                script_name="preprocess/"
                                            "preprocess_os_cmd_aml.py",
                                name="Preprocess Data with OS cmd",
                                compute_target=ANY)

    assert spy_pythonscriptstep_create.call_args[1]['arguments'][0] ==\
        '--dataset_name'
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][1] ==\
        e.dataset_name
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][2] ==\
        '--datastore_name'
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][3] ==\
        e.datastore_name

    # Check if Pipeline instantiation was called correctly
    spy_pipeline_create.assert_called_once_with(workspace=workspace,
                                                steps=ANY)
    assert spy_pipeline_create.call_args[1]['steps'][0]._runconfig ==\
        spy_pythonscriptstep_create.call_args[1]['runconfig']
    assert spy_pipeline_create.call_args[1]['steps'][0]._compute_target ==\
        spy_pythonscriptstep_create.call_args[1]['compute_target']

    # Check if Pipeline publish was called with arguments
    mock_pipeline_publish.\
        assert_called_once_with(name=e.preprocessing_pipeline_name,
                                description="Data preprocessing"
                                            " OS cmd pipeline",
                                version=e.build_id)


def test_build_data_processing_os_cmd_pipeline_default_datastore(
    mocker: MockFixture,
    environment_vars,     # NOQA: F811
    aml_pipeline_mocks):  # NOQA: F811
    """ Test Processing Pipeline build
        test branch get default datastore
    """
    # Load mocks and data objects from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks

    # Reset datastore_name from env_variables
    type(environment_vars).datastore_name =\
        mocker.PropertyMock(return_value=None)
    # From https://realpython.com/python-data-structures/#collectionsnamedtuple-convenient-data-objects  # NOQA: E501
    def_datastore_name = 'default_datastore'
    Def_datastore = namedtuple("Def_datastore", "name")
    ddi = Def_datastore(def_datastore_name)
    # Mock return value of aml_workspace.get_default_datastore().name
    mocker.patch('azureml.core.Workspace.get_default_datastore',
                 return_value=ddi)

    # Create Spies
    spy_pythonscriptstep_create =\
        mocker.patch('azureml.pipeline.steps.PythonScriptStep',
                     wraps=PythonScriptStep)
    spy_pipeline_create = mocker.patch('azureml.pipeline.core.Pipeline',
                                       wraps=Pipeline)

    # run as module (start from if __name__ == "__main__")
    runpy.run_module('ml_service.pipelines.'
                     'build_data_processing_os_cmd_pipeline',
                     run_name='__main__')
    # Assertions

    # Load Mocked environment variables
    e = Env()

    # Check if the correct workspace retrieved
    mock_workspace_get.assert_called_with(name=e.workspace_name,
                                          resource_group=e.resource_group,
                                          subscription_id=e.subscription_id)

    # Check if PythonScriptStep instantiation was called correctly
    spy_pythonscriptstep_create.\
        assert_called_once_with(allow_reuse=False,
                                runconfig=ANY,
                                arguments=ANY,
                                source_directory=e.sources_directory_train,
                                script_name="preprocess/"
                                            "preprocess_os_cmd_aml.py",
                                name="Preprocess Data with OS cmd",
                                compute_target=ANY)

    assert spy_pythonscriptstep_create.call_args[1]['arguments'][0] ==\
        '--dataset_name'
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][1] ==\
        e.dataset_name
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][2] ==\
        '--datastore_name'
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][3] ==\
        def_datastore_name

    # Check if Pipeline instantiation was called correctly
    spy_pipeline_create.assert_called_once_with(workspace=workspace,
                                                steps=ANY)
    assert spy_pipeline_create.call_args[1]['steps'][0]._runconfig ==\
        spy_pythonscriptstep_create.call_args[1]['runconfig']
    assert spy_pipeline_create.call_args[1]['steps'][0]._compute_target ==\
        spy_pythonscriptstep_create.call_args[1]['compute_target']

    # Check if Pipeline publish was called with arguments
    mock_pipeline_publish.\
        assert_called_once_with(name=e.preprocessing_pipeline_name,
                                description="Data preprocessing"
                                            " OS cmd pipeline",
                                version=e.build_id)


def test_build_data_processing_os_cmd_pipeline_exception_handling(
    mocker: MockFixture,
    aml_pipeline_mocks):  # NOQA: F811
    """ Test Processing Pipeline build
        test exception handling and logging case
    """
    # Load mocks and data objects from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks

    # Throw exception at Pipeline()
    mocker.patch('azureml.pipeline.core.Pipeline',
                 side_effect=ValueError('parameter unknown is not'
                                        ' recognized for Pipeline '))

    # Create Spies
    spy_pythonscriptstep_create =\
        mocker.patch('azureml.pipeline.steps.PythonScriptStep',
                     wraps=PythonScriptStep)
    # spy_pipeline_create = mocker.patch('azureml.pipeline.core.Pipeline',
    #                                    wraps=Pipeline)

    # run as module (start from if __name__ == "__main__")
    with pytest.raises(ValueError):
        runpy.run_module('ml_service.pipelines.'
                         'build_data_processing_os_cmd_pipeline',
                         run_name='__main__')

    # Assertions
    # Load Mocked environment variables
    e = Env()

    # Check if the correct workspace retrieved
    mock_workspace_get.assert_called_with(name=e.workspace_name,
                                          resource_group=e.resource_group,
                                          subscription_id=e.subscription_id)

    # Check if PythonScriptStep instantiation was called correctly
    spy_pythonscriptstep_create.\
        assert_called_once_with(allow_reuse=False,
                                runconfig=ANY,
                                arguments=ANY,
                                source_directory=e.sources_directory_train,
                                script_name="preprocess/"
                                            "preprocess_os_cmd_aml.py",
                                name="Preprocess Data with OS cmd",
                                compute_target=ANY)

    assert spy_pythonscriptstep_create.call_args[1]['arguments'][0] ==\
        '--dataset_name'
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][1] ==\
        e.dataset_name
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][2] ==\
        '--datastore_name'
    assert spy_pythonscriptstep_create.call_args[1]['arguments'][3] ==\
        e.datastore_name

    # Check if Pipeline publish was called with arguments
    mock_pipeline_publish.assert_not_called()
