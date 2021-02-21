import os
import json
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

from azureml.core import Workspace, Run
from azureml.core.authentication import MsiAuthentication
import azure.functions as func


def main(event: func.EventGridEvent):

    try:
        result = json.dumps({
            'id': event.id,
            'data': event.get_json(),
            'topic': event.topic,
            'subject': event.subject,
            'event_type': event.event_type
        })
        logging.info('PipelineRunMonitor: processed an event: %s', result)

        if (event.event_type == "Microsoft.MachineLearningServices.RunCompleted" or event.get_json()["runStatus"] == "Failed"):

            # Retrieve environment variables
            subscriptionId = os.environ["SUBSCRIPTION_ID"]
            rg_name = os.environ["RESOURCE_GROUP"]
            ws_name = os.environ["WORKSPACE_NAME"]
            app_insights_connection_string = os.environ["APP_INSIGHTS_CONNECTION_STRING"]

            # Managed identity authentication
            msi_auth = MsiAuthentication()

            # Azure ML workspace
            aml_workspace = Workspace(subscription_id=subscriptionId,
                                      resource_group=rg_name,
                                      workspace_name=ws_name,
                                      auth=msi_auth
                                      )
            logging.info(f"Azure ML workspace: {aml_workspace}")

            # Set up logger for Application Insights
            logger = logging.getLogger(__name__)
            logger.addHandler(AzureLogHandler(
                connection_string=app_insights_connection_string)
            )

            aml_run = Run.get(aml_workspace, event.get_json()["runId"])
            custom_dimensions = {
                "parent_run_id": aml_run.parent.id if aml_run.parent else aml_run.id,
                "parent_run_name": aml_run.parent.name if aml_run.parent else aml_run.name,
                "parent_run_number": aml_run.parent.number if aml_run.parent else aml_run.number,
                "run_number": aml_run.number,
                "step_id": aml_run.id,
                "step_name": aml_run.name,
                "experiment_name": aml_run.experiment.name,
                "run_url": aml_run.parent.get_portal_url() if aml_run.parent else aml_run.get_portal_url(),
                "parent_run_status": aml_run.parent.status if aml_run.parent else aml_run.status,
                "run_status": aml_run.status,
                "type": "run_detail",
                "workspace_name": aml_run.experiment.workspace.name
            }
            details = aml_run.get_details()
            logger.info(json.dumps(details, default=lambda o: ''), extra={'custom_dimensions': custom_dimensions})

        elif (event.event_type == "Microsoft.MachineLearningServices.RunStatusChanged" and event.get_json()["runStatus"] == "Running" and event.get_json()["runProperties"]["azureml.runsource"] == "azureml.PipelineRun"):
            # Please write a pipeline run notification here
            pass
    except Exception as ex:
        logging.exception(f"PipelineRunMonitor: stopped execution due to the following error: {ex}")
        raise Exception("PipelineRunMonitor error") from ex
