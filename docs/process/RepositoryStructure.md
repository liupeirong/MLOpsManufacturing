# Repository Structure

This repo contains sample code and definition of Azure DevOps pipelines for CI/CD. These pipelines run in this
[Azure DevOps project](https://dev.azure.com/cse-manufacturing/MLOpsManufacturing/_build?view=folders).
Azure ML pipelines run in the Azure environment deployed using the Azure DevOps pipelines.

## Folder structure

```bash
├─ common # contains tools and code cross-cutting samples
│
├─ docs # how-tos and best practices
│ 
├─ samples # each sample may have different folders, below is a typical example
│    ├─ <sample 1>
│    │    ├─ .devcontainer # VSCode dev container you can optionally use for development
│    │    ├─ data # store data for the sample if necessary
│    │    ├─ devops_pipelines # Azure DevOps CI/CD pipeline definition
│    │    ├─ environment_setup # Sample specific additional infrastructure setup
│    │    │      ├─ azureml_environment # Azure ML Environment Dockerfile
│    │    │      └─ provisioning # Additioal setup scripts for the sample
│    │    ├─ local_development # scripts for creating a local dev environment without having to have a VSCode dev container
│    │    ├─ ml_model # code for building the ML model
│    │    ├─ ml_service # code for building ML pipelines
│    │    ├─ tests # unit test code
│    │    │      ├─ ml_model
│    │    │      └─ ml_service
│    │    └─ README.md # explains what the sample is demonstrating and how to run it
│    └─ <sample 2>
│         └─ # same as above
├─ .gitattributes
├─ .gitignore
├─ LICENSE
└─ README.md
```

## Add new sample

When you add new sample:

- Follow same folder structure
- Use common as much as possible to avoid duplicate
- Feel free to add additional folders if necessary
