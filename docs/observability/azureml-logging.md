This wiki illustrates logging design for Azure ML.

- [Overview](#anchor0)
- [Logging information](#anchor1)
    - Logs pattern code example
    - Where to see
- [Azure App Insights](#anchor2)
    - Send logs to Azure App Insights and query with Kusto
    - Create a Dashboard

<a id="anchor0"></a>
# <a href="#anchor0">Overview</a>

|Where to log|What to log (examples)|Where from|
|-|-|-|
|Local (on demand)|Execution (console) logs during running pipeline |Python script for each step (if any)|
|Azure DevOps|- Execution (console) logs during building and publishing pipeline|Azure ML pipeline build script|
|Azure ML|- Execution (console) logs during running pipeline <br>- Result of model performance testing|Azure ML pipeline step scripts|
|Azure App Insights|- Additional information to identify the detail of pipeline run <br>- Result of model performance testing<br>- Pipeline run duration and status|Azure ML pipeline step scripts<br> Azure Function *1 |


*1 We cannot get run duration detail from each step, therefore we use Azure Function to query run duration and status results when each step completed/failed, which is triggered by EventGrid.

<a id="anchor1"></a>
# <a href="#anchor1">Logging information</a>

## Logs pattern code example
```
[logging.formatter]

    - Default:
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    e.g. 2020-11-30 05:57:14,574 - __main__ - INFO - prune parameter: 0 2
```
## Where to see
### Azure DevOps
![azureml-logging-01.png](../media/azureml-logging-01.png)

### Azure ML
You can find logs on "Outputs + logs" pane under "Experiments" on Azure ML studio.

### Azure storage
Azure ML output log automatically store in Azure ML blob storages.


<a id="anchor2"></a>
# <a href="#anchor3">Azure App Insights</a>
Since logs from Python wrapper are already logged in Azure ML it would be better to log only additional information to Azure App Insights.
The difference from logs in Azure ML is to send only required logs by reducing the amount of info.

## Send logs to Azure App Insights and query with Kusto
There is a sample demonstrates how to send logs to Azure App Insights by using Function App and query with Kusto. See [pipeline monitor sample](../../common/pipeline_monitor/README.md) for more detail. 

## Create a Dashboard
Dashboard is useful to centralize logs and status easily. See [Azure Dashboard]() document for more detail.
