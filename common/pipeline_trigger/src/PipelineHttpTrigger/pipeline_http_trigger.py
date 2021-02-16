import logging
import os

import azure.functions as func
from azureml.core import Workspace
from azureml.core.authentication import MsiAuthentication
from azureml.pipeline.core import PipelineEndpoint


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Retrieve environment variables
    subscriptionId = os.environ["SUBSCRIPTION_ID"]
    rg_name = os.environ["RESOURCE_GROUP"]
    ws_name = os.environ["WORKSPACE_NAME"]
    pipeline_endpoint_name = os.environ["PIPELINE_ENDPOINT_NAME"]
    experiment_name = os.environ["EXPERIMENT_NAME"]

    # Managed identity authentication
    msi_auth = MsiAuthentication()

    # Azure ML workspace
    aml_workspace = Workspace(subscription_id=subscriptionId,
                              resource_group=rg_name,
                              workspace_name=ws_name,
                              auth=msi_auth
                              )
    logging.info(f"Connected to workspace: {aml_workspace}")

    try:

        # Submit a job to a pipeline endpoint
        pipeline_endpoint_by_name = PipelineEndpoint.get(workspace=aml_workspace, name=pipeline_endpoint_name)
        run_id = pipeline_endpoint_by_name.submit(experiment_name)
        logging.info(f"Pipeline Endpoint: {run_id}")
        logging.info("Successfully submit a job to the default version of a pipeline endpoint")
        return func.HttpResponse(f"run_id: {run_id}")

    except Exception as ex:
        logging.exception(f'main function stopped execution due to the following error: {ex}')
