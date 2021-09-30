<!-- omit in toc -->
# Model Monitoring

When a model is deployed, it is important to understand how well the predictions are matching the expected outputs in the live system.
This generally entails some manner of gathering live data from the system and evaluating the model predictions against ground truth.

<!-- omit in toc -->
## Table of Contents

- [Monitoring Function](#monitoring-function)
- [Azure Monitor Alert](#azure-monitor-alert)
  - [Deploying the Alert](#deploying-the-alert)

## Monitoring Function

To implement this monitoring, the current system employs an [Azure Function](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview)
application deployed in a resource group with read access to the blob storage where prediction data is uploaded.
This Function application monitors the blob storage container, and when new data is uploaded (with the lab results already merged),
it reads in that blob data and compares the prediction result to the lab measurement,
then outputs its reading to [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview).

As of 9/16/2021, the function code currently calculates the `RMSE` value between the ground truth and the ML Model prediction
columns. This information is then logged both as a string to Application Insights, as well as additional properties
attached to the log itself, to enable filtering queries.

## Azure Monitor Alert

Within the Application Insights system, an alert has been configured to validate that the `RMSE` value for a given
day does not exceed a specified threshold. The alert uses a log query (using the KQL) to
filter the logs from the Azure Function, and aggregate logs based on the `RMSE` value.

An example query looks like this:

```Kusto
traces # Logs from the function are considered 'traces'
| where customDimensions has "rmse" # CustomDimensions are the values that are passed to "extras" in the Azure Function log
| extend rmse = todynamic(tostring(customDimensions.rmse)) # 'extend' creates a new column based on the property
| where rmse > 0.06 # only returns logs where the RMSE value is above 0.06
```

Additionally, developers could extend more properties, such as `line` or `plant` to filter the alerts further.

Once a day, the alert runs the query, and if any logs match the query, an alert is sent to the specified
[Azure Action Group](https://docs.microsoft.com/en-us/azure/azure-monitor/alerts/action-groups) as an email
(this can be configured to instead be an SMS, or Push notification as well).

### Deploying the Alert

The alert is deployed via an Arm template, located in
[mlops\monitoring\app_insights_queries](./monitoring/app_insights_queries).
The `model-monitor-alert.json` file specifies the template for the deployment, while the `alert.parameters.json`
file specifies the specifics of the deployment.

Using the `az deployment group create` method, developers can manually (or as a part of CI/CD) deploy the
alert. The parameters can be passed from the json file, or manually overwritten at the time of running
the deployment command.

Current Parameters:

```json
        //  The name of the Alert
        "scheduledqueryrules_name": {
            "type": "String"
        },
        // The full Resource ID string for the Application Insights Instance
        // Follows the format: /subscriptions/<SUBSCRIPTION ID>/resourceGroups/<RESOURCE GROUP>/providers/microsoft.insights/components/<APP INSIGHTS INSTANCE NAME>
        "resourceId": {
            "type": "String"
        },
        // The full Resource ID string for the Action Group
        "actionGroups_model_owners": {
            "type": "String"
        },
        // Description of the Alert
        "alertDescription": {
            "defaultValue": "This alert checks for a specified metric to be below a given value",
            "type": "String"
        },
        // Number based alert severity, with 0 being the most severe
        "alertSeverity": {
            "type": "int",
            "defaultValue": 3,
            "allowedValues": [
                0,
                1,
                2,
                3,
                4
            ]
        },
        // Specifies if the alert is enabled upon deployment
        "isEnabled": {
            "type": "bool",
            "defaultValue": true
        },
        // The Kusto query that identifies what logs set off an alert
        "alertQuery": {
            "type": "string"
        },
        // Period of time used to monitor alert activity based on the threshold. Must be between one minute and one day. ISO 8601 duration format.
        "windowSize": {
            "type": "string",
            "defaultValue": "P1D"
        },
        // How often the metric alert is evaluated represented in ISO 8601 duration format
        "evaluationFrequency": {
            "type": "string",
            "defaultValue": "P1D"
        }
```
