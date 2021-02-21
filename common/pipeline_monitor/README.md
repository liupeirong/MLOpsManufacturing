<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#repo-structure">Repo Structure</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#analyze-run-result">Analyze run result</a></li>
    <li><a href="#references">References</a></li>
  </ol>
</details>

<!-- Overview -->
# Overview
When using Azure Machine Learning(AML) Service, there are cases when it is necessary to monitor AML pipeline run results. This sample demonstrates how to retrieve such data and load into Application Insights so that you can create dashbaord from logs.
1. Receive Machine Learning service Event

    See more details [here](https://docs.microsoft.com/en-us/azure/event-grid/event-schema-machine-learning?tabs=event-grid-event-schema#microsoftmachinelearningservicesruncompleted-event)
1. Get run id from Event
1. Get run details by using run id which contains following information:
    - runId: ID of this run.
    - target
    - status: The run's current status. Same value as that returned from get_status().
    - startTimeUtc: UTC time of when this run was started, in ISO8601.
    - endTimeUtc: UTC time of when this run was finished (either Completed or Failed), in ISO8601.
    This key does not exist if the run is still in progress.
    - properties: Immutable key-value pairs associated with the run. Default properties include the run's snapshot ID and information about the git repository from which the run was created (if any). Additional properties can be added to a run using add_properties.
    - inputDatasets: Input datasets associated with the run.
    - outputDatasets: Output datasets associated with the run.
    - logFiles
    - submittedBy

     See more details [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.run(class)?view=azure-ml-py#get-details--) 
1. Get additional information from run context and store them in custom dimensions.
    ```python
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
    ```
1. Send them to app insights

The reason why custom dimensions is added is that run details are not enough to query results in real projects.

**What does this sample demonstrate:**
- How to retrieve AML pipeline run results via Azure Function

**What doesn't this sample demonstrate:**
- Azure Machine Learning Service Creation.


<!-- REPO STRUCTURE -->
# Repo Structure

This repo contains sample code to monitor Azure ML pipelines via Azure Functions.

The folders are structured as following - 
```
common
  └── pipeline_monitor
        ├── devops_pipelines # Azure DevOps CI/CD pipeline definition
        ├── environment_setup # Azure DevOps IaC pipeline definition to provision Azure resources
        ├── media # images for README
        │
        ├── src
        │    ├── PipelineRunMonitor # scripts for Event Grid trigger function
        │    ├── .funcignore
        │    ├── host.json
        │    ├── local.settings.json.example
        │    └── requirements.txt
        │
        ├── tests
        │      └── src
        │           └── PipelineRunMonitor
        │                    └── test_pipeline_run_monitor.py # unit test for Event Grid trigger
        │
        ├── .flake8 # configuration file for linter flake8
        ├── .gitattributes
        ├── .gitignore
        └── README.md # explains what the sample is demonstrating and how to run it
```

<!-- ABOUT THE FOLDER -->
## About The Folder
This `pipeline_monitor` folder contains source code for one Azure Functions below:

|Function|Purpose|
|-|-|
|PipelineRunMonitor|Event Grid trigger - This function will be triggered when AML pipeline status changed event.|


<!-- GETTING STARTED -->
# Getting Started

- [Prerequisites](#Prerequisites)
- [Configure Azure Machine Learning Event](#Configure-Azure-Machine-Learning-Event)

## Prerequisites

- [Create Azure Resources](#Create-Azure-Resources)
- [Install Tools](#Install-Tools)

### Create Azure 

In this step, you will create Azure resources such as Azure Machine Learning and Function App. In addition you will set up permission for the function to access to Azure Machine Learning workspace.

1. This code needs to get Azure ML context for remote or offline runs. Create Azure resources as documented [here](../../common/infrastructure/README.md).

1. Create additional Application Insights if you want to store pipeline run data separately. You can also reuse the application insights created in step above.

1. Create Function App by using following settings:

    - Runtime: Python 3.8
    - Publish: Code

1. Once the Function App is created, go to the resource and select **Identity**.

1. Enable **System assigned** managed identity and save.

1. Go to Azure Machine Learning resource and select **Access Control(IAM)**

1. Add **masterreader** role to service principal which is same name as the Function App.

### Install Tools

1. Install [Azure CLI version 2.4 or later](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).

1. Install [Azure Functions Core Tools version 3.x](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#v2).

1. Python 3.8 (64-bit), Python 3.7 (64-bit), Python 3.6 (64-bit), which are all supported by version 3.x of Azure Functions. As this sample uses Python 3.8, make sure by running `python --version` (Linux/macOS) or `py --version` (Windows) to check your Python version reports 3.8.x.

1. Install pip packages
    ```sh
    $ pip install -r requirements.txt
    ```

## Configure Azure Machine Learning Event 

Once you completed prerequisites, configure the Azure Machine Learning Event.

- [Deploy the function project to Azure](#Deploy-the-function-project-to-Azure)
- [Configure Events](#Configure-Events)

### Deploy the function project to Azure
1. Install [Azure CLI 2.4 or later](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli). Make sure to check the version by running `az --version`.

1. Login to Azure:
    ```sh
    $ az login
    ```

1. Check which subscription you are currently using:
    ```sh
    $ az account show -o table
    ```

    If you are not in the subscription you want to use, use `az account set -s [subscription id]` to switch.
    You can also use ```az account list``` to get all the subscription id.

1. Change directory to src directory.

    ```sh
    cd common/pipeline_monitor/src
    ```

1. Deploy your local functions project by using the `func azure functionapp publish` command. Replace <APP_NAME> with the name of your app.
    ```sh
    $ func azure functionapp publish <APP_NAME>
    ```
### Configure Events

This function is triggered when Azure Machine Learning Events are issued. You can easily configure the event by following steps below:

1. Open Azure Machine Learning resource from Azure Portal.

1. Select **Events** menu.

1. Click **+ Event Subscription**.

1. Enter Name nad System Topic Name.

1. Select **Run completed** and **Run status changed** from **EVENT TYEPS**

1. Select **Azure Function** in **Eventpoint Type** and click **Select an endpoint**.

1. Select created Azure Function app and **PipelineRunMonitor** function.

1. Complete the wizard by creating it.

# Analyze run result

Once you completed deployment, you can analyze the run result.

## Run Azure Machine Learning pipeline

First of all, run any Azure Machine Learning pipeline and confirm the Fuction is triggered.

## Query Application Insights

It may take up to five minutes until the log is sent to Application Insights. 

1. Open Application Insights resource.

1. Select **Logs** in **Monitoring section**.

1. Run Kusto query after replace variable and see the results. This query calculates pipeline step duration by using `startTimeUtc` and `endTimeUtc`. It also projects (selects) experiment name and workspace name from custom dimensions.

    ```sh
    let experiment_name = '<your experiment name>';
    let workspace_name = '<your workspace>';
    traces
    | project data = parse_json(message), customDimensions, timestamp
    | project 
        experiment_name = tostring(customDimensions.experiment_name),
        workspace_name = tostring(customDimensions.workspace_name),
        run_number = tostring(customDimensions.run_number),
        steps = iif(tostring(customDimensions.parent_run_id) == tostring(customDimensions.step_id), "total", customDimensions.step_name),
        duration = datetime_diff('second', todatetime(data.endTimeUtc), todatetime(data.startTimeUtc)), 
        parent_run_number = tostring(customDimensions.parent_run_number), 
        customDimensions,
        timestamp
    | where customDimensions.type == 'run_detail' and parent_run_number != '' and steps != 'total' and experiment_name == experiment_name and workspace_name == workspace_name
    | summarize arg_max(timestamp, *) by run_number
    | sort by run_number asc
    ```
1. Run the query and see the result.

## Custom Dimensions

Kusto query support custom dimensions where you can store additional information. This sample stores all run detail inforamtion in custom dimensions and project in Kusto query.

Values in Custom Dimensions are **dynamic** type, so you need to explicitly convert it to desired type by using **tostring** or **toint**.

It also calcuate duration by using startTimeUtc and endTimeUtc, which comes as part of Event Grid event from Azure Machine Learning events.

See [Azure Machine Learning as an Event Grid source](https://docs.microsoft.com/en-us/azure/event-grid/event-schema-machine-learning) for more detail.

<!-- REFERENCES -->
# References

* [Quickstart: Create a Python function in Azure from the command line](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=azure-cli%2Cbash%2Cbrowser)
* [Azure Functions Python developer guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
* [Getting started with Kusto](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/concepts/)
* [Azure Machine Learning as an Event Grid source](https://docs.microsoft.com/en-us/azure/event-grid/event-schema-machine-learning)