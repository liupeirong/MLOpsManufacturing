# Overview

We use Azure DevOps pipeline to achieve CI/CD for MLOps. It supports various features to cover many scenarios.

- Trigger
- Template
- Logging
- Rich UI

## Pipeline Strategy

### Trigger

Even though Azure DevOps pipeline supports implicit trigger which we can omit trigger section, we explicitly describe trigger in each pipeline YAML to have full control when an Azure DevOps pipeline runs.

We also use "include" keywords first, then use "exclude" if necessary in sub-folders/files.

```yaml
trigger:
  branches:
    include:
    - main
  paths:
    include:
    - samples/yesno/ml_model
    - samples/yesno/ml_service
```

### Templated YAML

Azure DevOps support templating some tasks for re-usability. We use templated YAML to avoid duplicate code. Templated YAML file contains '-template' as part of its name.

### Code Quality

Each Azure DevOps pipelines should include code quality check and publish the test results so that operators can confirm it via portal

Sample contains code-quality-template.yml to demonstrate:

- Run linter and generate report
- Run unit test and generate report
- Publish test result
- Publish code coverage report

This is templated yaml so that we can easily reuse the yaml in multiple pipelines.

### Variables

Azure DevOps support variables YAML as templated YAML which contains only variables and can be re-used in multiple pipelines. Variable YAML file contains '-variables' as part of its name.

```yaml
variables:
- template: yesno-variables-template.yml
```

### Variable from KeyVault

We store secure variables in KeyVault and use KeyVault task to retrieve the value. We use explicit filter criteria to only retrieve required variables form the KeyVault

```yaml
- task: AzureKeyVault@1
    displayName: Azure Key Vault
    inputs:
    azureSubscription: '$(AZURE_RM_SVC_CONNECTION)'
    keyVaultName: '$(KEYVAULT_NAME)'
    secretsFilter: aml-storage-account-key,acr-password
    runAsPreJob: false
```

### Azure DevOps Pipeline Library

Some variables reside in Azure DevOps Pipeline Library, which we can set pipeline to read them by using **group** for **variables**

```yaml
variables:
- group: iac-aml-vg
```

### Service Connection

Azure DevOps supports service connection to simplify authentication process for various Azure resources. We use service connection for Azure Resource Group.

### Stages

Azure DevOps pipeline support stage concept by which we can group related tasks into a stage. We use stage to distinguish test, deploy to dev and deploy to stage. See [Azure DevOps Stages](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/stages?view=azure-devops&tabs=yaml) for more detail.

## Pool

Azure DevOps pipeline uses virtual machines to run the pipeline. Microsoft provides Microsoft-hosted agents as pool, and you can also provision own VM as self-hosted agents.

If you run long running build process, like build docker image, you can create your own agent and register it as pool. See [Azure Pipelines agents](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=browser) for more detail.
