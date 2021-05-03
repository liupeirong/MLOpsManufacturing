[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/observability-library/observability-lib-ci?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=44&branchName=main)
[![Build Status](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_apis/build/status/observability-library/observability-lib-cd?branchName=main)](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build/latest?definitionId=45&branchName=main)

# Overview

Logs text and metrics in Azure ML, App Insights, and console with a single call. Also supports tracing in App Insights.

> Disclaimer: This package is built by Microsoft engineers, but it is not an officially supported Microsoft package.

# How to use

## 1. Add dependencies

The following dependencies are required to use this package.

```yaml
  - python-dotenv==0.15.*
  - dataclasses==0.*
  - opencensus==0.7.*
  - opencensus-context==0.1.*
  - opencensus-ext-azure==1.0.*
  - opencensus-ext-logging==0.1.*
  - opencensus-ext-httplib==0.7.*
```

## 2. Configure environment variables to control logger behavior

```bash
# AppInsights logger is enabled if this is a valid connection string
APPLICATIONINSIGHTS_CONNECTION_STRING = ''
# Console logger is enabled if set to 'true', default to 'true'
LOG_TO_CONSOLE = 'false'
# Azure ML logger is enabled when running as an experiment in Azure ML
# DEBUG, INFO, WARNING, ERROR, CRITICAL, default is WARNING
LOG_LEVEL = 'WARNING' 
# Probability 0.0 -> 1.0
LOG_SAMPLING_RATE = '1.0'
# Probability 0.0 -> 1.0
TRACE_SAMPLING_RATE = '1.0'
# Frequency in seconds to send metric to App Insights, default is 15
METRICS_EXPORT_INTERVAL = '15'
# Whether to log App Insights standard machine metrics, CPU, memory etc, default to 'false'
ENABLE_STANDARD_METRICS = 'true'
```

## 3. Log messages and metrics

```python
from azureml_appinsights_logger.observability import Observability
from azureml_appinsights_logger.logger_interface import Severity

logger = Observability()

def main():
  logger.log("Hello")
  logger.log("Something is wrong", severity=Serverity.ERROR)
  logger.log_metric(name="metric1", value=100)
  logger.log_metric(name="metric2", value=200, log_parent=True)
  try:
    raise Exception("error")
  except Exception as ex:
    logger.exception(ex)
  
  # allow time for appinsights exporter to send metrics every EXPORT_INTERVAL seconds
  time.sleep(30)


if __name__ == '__main__':
  logger.start_span('train_aml')
  try:
    main()
  except Exception as exception:
    logger.exception(exception)
    raise exception
  finally:
    logger.end_span()
```

## 4. Query logs and metrics

### correlation_id

The correlation_id is used to map specific Azure ML experiment run with the logs and metrics.
Correlation_id is added to telemetry processor as a custom dimension in the following steps:

* When logging in an Azure ML experiment run, the correlation_id is the Azure ML *Run Id*
* When logging outside of an Azure ML experiment run, the correlation_id is the *BUILD_ID* environment variable
* When logging outside of an Azure ML experiment run, and there's no *BUILD_ID* environment variable, it's set to a unique identifier

### Check metrics in Azure ML

Navigate to [Azure ML portal](https://ml.azure.com/), find the target experiment and run.
In the *Metrics* tab you can see the logged metrics.
![Metrcis](/common/azureml_appinsights_logger/media/metrics.png)

### Check metrics in AppInsights

Navigate to Application Insights in the Azure portal.
Click on *Logs* tab and select *Custom Metrics*.
You may use the below queries to retrieve all metrics:

```sql
customMetrics
```

To narrow your search to the specific run you can provide the correlation_id:

```sql
customMetrics 
| where customDimensions.correlation_id contains "e56b31b7-513f-4c34-9158-c2e1b28a5aaf" 
```

![metrics-appInsights](/common/azureml_appinsights_logger/media/metrics-appinsights.png)

### Check logs in Azure ML

When running as an experiment in Azure ML, logs will be sent to Azure ML.
You can check the logs by logging in to [Azure ML portal](https://ml.azure.com/) portal.
Then click on the target experiment and run. If there are child runs, select the specific child run.
click on *Outputs + logs* tab and check the logs.

Logs are in the following format:

```text
timeStamp, [severity], callee_file_name:line_number:description
```

![logs-aml](/common/azureml_appinsights_logger/media/logs-aml.png)

### Check logs in Application Insights

Navigate to Application Insights in the Azure Portal. Click on *Logs* tab and select *Traces*.
You may use the below queries to retrieve your logs:

```sql
traces
```

To narrow the search to the specific run, provide the correlation_id:

```sql
traces
| where customDimensions.correlation_id contains "e56b31b7-513f-4c34-9158-c2e1b28a5aaf"
```

![logs-appInsights](/common/azureml_appinsights_logger/media/logs-appinsights.png)

## Dependency Tracing (spans)

Dependencing tracing is most useful in an ML inferencing application.
It will trace the incoming request down its dependency services and is only available in App Insights.
Call `start_span` and `end_span` around the code you want to trace.
To view the dependency map, navigate to App Insights portal, select *Application map* tab.
![span-appInsights](/common/azureml_appinsights_logger/media/span-appinsights.png)
