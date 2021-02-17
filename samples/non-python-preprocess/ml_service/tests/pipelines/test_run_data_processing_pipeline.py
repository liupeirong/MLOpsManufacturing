import runpy
from pytest_mock import MockFixture
from easydict import EasyDict as edict
from ml_service.tests.pipelines.test_aml_mock_fixtures_env import environment_vars, aml_pipeline_mocks  # NOQA: F401, E501


def test_run_data_processing_pipeline_happy_path(mocker: MockFixture,
                                                 aml_pipeline_mocks):  # NOQA: F811, E501

    """ Test Processing Pipeline build
        happy Path
    """
    # Load mocks from fixture
    (workspace, aml_compute, mock_workspace_get, mock_pipeline_publish) =\
        aml_pipeline_mocks

    mock_args = mocker.patch('argparse.ArgumentParser.parse_args')
    mock_args.return_value = edict({"aml_pipeline_name": "aml_pipeline_name_test",  # NOQA: E501
                                    "output_pipeline_id_file": "w",
                                    "skip_preprocessing_execution": False})

    mock_aml_pipelines_list = mocker.patch('azureml.pipeline.core.PublishedPipeline.list')  # NOQA: E501
    type(mock_pipeline_publish).name = mocker.PropertyMock(return_value='aml_pipeline_name_test')  # NOQA: E501
    type(mock_pipeline_publish).id = mocker.PropertyMock(return_value='1')
    mock_aml_pipelines_list.return_value = [mock_pipeline_publish]
    mocker.patch('azureml.core.Experiment')

    # run as module (start from if __name__ == "__main__")
    runpy.run_module('ml_service.pipelines.'
                     'run_data_processing_pipeline',
                     run_name='__main__')
