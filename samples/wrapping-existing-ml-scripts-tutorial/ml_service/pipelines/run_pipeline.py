
from azureml.core import Workspace, Experiment
from azureml.pipeline.core import PipelineEndpoint
from ml_service.util.env_variables import Env
import argparse

"""
$ python -m ml_service.pipelines.run_pipeline --test_size=0.2
"""

if __name__ == "__main__":
    # Environment variables
    env = Env()

    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_size', type=float, default=0.2)
    args = parser.parse_args()

    # get workspace
    ws = Workspace.from_config()
    exp = Experiment(workspace=ws, name=env.aml_experiment_name)

    # customize parameters
    custom_pipeline_parameters = {
        "pipeparam_test_size": args.test_size
    }
    print('custom_pipeline_parameters=', custom_pipeline_parameters)

    # run pipeline
    pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name=env.aml_pipeline_endpoint_name)
    pipeline_run = exp.submit(pipeline_endpoint, pipeline_parameters=custom_pipeline_parameters)

    # print url
    aml_url = pipeline_run.get_portal_url()
    print(aml_url)
