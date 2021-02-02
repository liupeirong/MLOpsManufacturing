import pytest
import runpy
from pytest_mock import MockFixture
from unittest.mock import ANY
from ml_service.tests.pipelines.test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks
from ml_service.util.env_variables import Env
from azureml.pipeline.core import Pipeline
from azureml.pipeline.steps import PythonScriptStep
from collections import namedtuple


def test_run_data_processing_pipeline_happy_path(mocker: MockFixture, aml_pipeline_mocks):

    """ Test Processing Pipeline build
        happy Path
    """

    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) = aml_pipeline_mocks
    
    # Create Spies
    spy_published_pipeline_create = mocker.patch('azureml.pipeline.core.PublishedPipeline', wraps=PublishedPipeline)

    runpy.run_module('ml_service.pipelines.'
                     'run_data_processing_pipeline',
                     run_name='__main__')

    e = Env()
    mock_workspace_get.assert_called_with(name=e.workspace_name,
                                          resource_group=e.resource_group,
                                          subscription_id=e.subscription_id)

    spy_published_pipeline_create.assert_called_once_with(workspace=workspace)

