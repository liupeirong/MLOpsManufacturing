# import pytest
import runpy
from pytest_mock import MockFixture
# from unittest.mock import ANY
from ml_service.tests.pipelines.test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks  # NOQA: F401, E501
from azureml.pipeline.core import PublishedPipeline
from azureml.pipeline.core import Pipeline
from ml_service.pipelines.run_data_processing_pipeline import main

# from ml_service.util.env_variables import Env
# from azureml.pipeline.core import Pipeline
# from azureml.pipeline.steps import PythonScriptStep
# from collections import namedtuple
import argparse
import sys


def test_run_data_processing_pipeline_happy_path(mocker: MockFixture, 
                                                 aml_pipeline_mocks):  # NOQA: F811, E501

    """ Test Processing Pipeline build
        happy Path
    """
    # Load mocks from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks

    # # Create Spies
    # spy_parser_create = mocker.patch('argparse.ArgumentParser')
    # # spy_pipeline_create = mocker.patch('azureml.pipeline.core.Pipeline',
    # #                                    wraps=Pipeline)
    spy_pipeline_create = mocker.patch('azureml.pipeline.core.Pipeline',
                                wraps=Pipeline)
    spy_published_pipeline_create = mocker.patch('azureml.pipeline.core.PublishedPipeline.list', wraps=PublishedPipeline)
    # # spy_published_pipeline_create.list(workspace)
    # # matched_pipes.append(mock_pipeline_publish)


    # run as module (start from if __name__ == "__main__")
    main()
    # runpy.run_module('ml_service.pipelines.'
    #                  'run_data_processing_pipeline',
    #                  run_name='__main__')


    # e = Env()

    # # spy_parser_create.assert_called_once_with()

    # mock_workspace_get.assert_called_with(name=e.workspace_name,
    #                                       resource_group=e.resource_group,
    #                                       subscription_id=e.subscription_id)

    # # spy_published_pipeline_create.assert_called_once_with(workspace=workspace)
    # # spy_published_pipeline_create.assert_called_with(workspace=workspace)
    # published_pipeline = mock_pipeline_publish
