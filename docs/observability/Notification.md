# Notification - Azure DevOps, Azure Machine Learning, and Cost Management

This document provides a short summary on setting up notifications in Azure.

## Notification

|Who|What|Where|How|Related document|
|-|-|-|-|-|
|Software Engineer, System Admin, Data Scientist|Azure DevOps pipeline<br>- Build completes<br>- Pull request reviewers added or removed<br>- Pull request changes|-email<br>-Microsoft Teams<br>-Slack|- email: Notifications setting in Azure DevOps (Personal, Team, Project, Global)<br>- [Azure DevOps Pipelines with Microsoft Teams](https://docs.microsoft.com/en-us/azure/devops/pipelines/integrations/microsoft-teams?view=azure-devops)<br>- [Azure DevOps Pipelines with Slack](https://docs.microsoft.com/en-us/azure/devops/pipelines/integrations/slack?view=azure-devops)|- Azure DevOps monitoring and notification (See the following section)<br>- [Azure Pipelines with Microsoft Teams](https://docs.microsoft.com/en-us/azure/devops/pipelines/integrations/microsoft-teams?view=azure-devops)<br> - [Microsoft Teams - Azure Pipelines](https://appsource.microsoft.com/en/product/office/wa200000055?src=wnblogmar2018)<br>- [Azure Pipelines with Slack](https://docs.microsoft.com/en-us/azure/devops/pipelines/integrations/slack?view=azure-devops)<br> - [Slack app - Azure Pipelines](https://slack.com/apps/AFH4Y66N9-azure-pipelines)|
|Data Scientist|Azure ML pipeline<br>-Success/Failure|-email<br>-Microsoft Teams<br>-Slack|- StorageQueue + LogicApp<br>- Directly set trigger with AML events e.g. LogicApp (See [document](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid))|-|
|QA (Quality Assurance)|Azure ML pipeline<br>- Start/End of experiments<br>- Where the result is (i.e. Azure Dashboard)|-email<br>-Microsoft Teams<br>-Slack |- StorageQueue + LogicApp<br>- Directly set trigger with AML events e.g. LogicApp (See [document](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid))<br>*QA team does not have access to Azure DevOps and Azure ML|- [Trigger applications, processes, or CI/CD workflows based on Azure Machine Learning events (preview)](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid)<br> - [Azure Machine Learning events (preview) section in Spike wiki - Notification](/Spikes/Notification)|
|Business Analyst|Cost management|-|- Azure Cost Management|[Azure Cost Management](https://docs.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview)|

## Azure DevOps monitoring and notification

### Personal

__Current Setting__
Open your profile menu, and choose Notifications,

![Azure-Devops-monitoring-and-notification-01.png](../media/observability/Azure-Devops-monitoring-and-notification-01.png)

Or Notification settings.

![Azure-Devops-monitoring-and-notification-02.png](../media/observability/Azure-Devops-monitoring-and-notification-02.png)

The profile menu appears as shown below based on whether the New Account Manager feature has been enabled or not.

![Azure-Devops-monitoring-and-notification-03.png](../media/observability/Azure-Devops-monitoring-and-notification-03.png)

### Team, Project

__Current Setting__
You can see the current **team or project level** notifications setting from Project Settings in Azure DevOps.

### Add new notifications

1. Click "New subscription" and select a templete
![Azure-Devops-monitoring-and-notification-04.PNG](../media/observability/Azure-Devops-monitoring-and-notification-04.PNG)

2. Input the detail and click "Finish"

### Deliver to individual members or specific email address

If you want to deliver not individual members but specific email address only, then you can change the delivery setting.

### Global

__Current Setting__
This Global setting is for both Language Model and Trigger Word projects.
Choose the Azure DevOps icon and then choose Global Notifications under Organization settings.

## Reference

- [About notifications](https://docs.microsoft.com/en-us/azure/devops/notifications/about-notifications?view=azure-devops)
- [Novigating the UI](https://docs.microsoft.com/en-us/azure/devops/notifications/navigating-the-ui?view=azure-devops)
- [Events and notifications](https://docs.microsoft.com/en-us/azure/devops/notifications/concepts-events-and-notifications?view=azure-devops)
- [How email recipients are determined](https://docs.microsoft.com/en-us/azure/devops/notifications/concepts-email-recipients?view=azure-devops)
- [Change your preferred email address](https://docs.microsoft.com/en-us/azure/devops/notifications/change-email-address?view=azure-devops&tabs=preview-page)
- [Manage personal notifications](https://docs.microsoft.com/en-us/azure/devops/notifications/manage-your-personal-notifications?view=azure-devops&tabs=preview-page)
- [Unsubscribe from default notification](https://docs.microsoft.com/en-us/azure/devops/notifications/unsubscribe-default-notification?view=azure-devops)
- [Manage team, group, and Global notifications](https://docs.microsoft.com/en-us/azure/devops/notifications/manage-team-group-global-organization-notifications?view=azure-devops)
- [Exclude your self from notification of events you initiated](https://docs.microsoft.com/en-us/azure/devops/notifications/exclude-self-from-email?view=azure-devops)
