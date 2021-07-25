# Overview

__What does this sample demonstrate:__
This sample demonstrates how to run unit tests on Python code using [Databricks Connect](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/databricks-connect), run integration tests on Databricks notebooks, and deploy a Databricks job, all in [GitHub Actions](https://docs.github.com/en/actions/learn-github-actions).

The sample contains a single notebook [main_notebook.py](src/main_notebook.py) which calls [some_function](test/dbcicdlib/some_func.py) in a Python module. We run [unit test on some_function](test/unittests/test_some_func.py) and [integration test on main_notebook.py](test/run_notebook_tests.sh).

This sample also shows how to [update the job if a job with the same name already exists](/.github/workflows/cicd.yml#L119). By default, if the CD pipeline publishes a job, it's a new job with a new job id even if another job with the same name already exists.

Another small feature used in this sample is to use a [pre-commit config hook](.pre-commit-config.yaml) to run [detect-secrets](https://github.com/Yelp/detect-secrets) to prevent secrets from being checked into code.

__What doesn't this sample demonstrate:__
Both the notebook and the library code are bare minimum sample code, not meant to represent real world business logic.

## How it works

Databricks Connect enables IDE such as VSCode and [Databricks Connect Cli](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/databricks-connect#step-1-install-the-client) tool to access Databricks cluster from the local dev machine or build agent. Unit tests should have no external dependencies such as dbfs, instead, they should be taking dataframes as input/output parameters. Once Databricks Connect is set up, you can run unit tests using PyTest as usual, either in the command line, or in VSCode. You can also debug Python scripts or unit tests in VSCode. If the target Databricks cluster is not running, it will be automatically started.

You can also run or debug Databricks Notebooks locally with Databricks Connect. However, in this example, we use [run_notebook_tests.sh](test/run_notebook_tests.sh) to create a [one time job run](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/jobs#--runs-submit) that invokes [test_main_notebook.py](test/test_main_notebook.py), which further invokes main_notebook.py and [asserts](test/test_main_notebook.py#L26) its output against expected results. The reasons we are not using Databricks Connect to run integration tests include:

1. In production, the code will run as Databricks Jobs. It's better to run the tests in a way as close to real environment as possible.
1. Typically you need to install your library code as modules for the job notebook or script to call. Once libraries are installed to the cluster, it takes a cluster restart to remove it. This makes tearing down the tests inefficient and if another test is run before the cluster restarts, the test result can't be trusted.

## How to run tests on the local dev machine

### Prereq

1. Set up a Conda environment for this project using [environment.yml](environment.yml):  `conda env create -f environment.yml`. Then activate this environment.
1. Install [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) in VSCode, open the root folder of this project, and [set up the Python environment](https://code.visualstudio.com/docs/python/environments) by selecting the interpreter, linter, and configuring tests with PyTests.
1. Copy [.env.sample](.env.sample) to your own `.env`, and set up the environment variables.

### Run unit tests

1. Set up Databricks Connect. Databricks Connect is already installed in the Conda environment mentioned in the Prereq section. It still needs to be configured as [documented](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/databricks-connect#requirements).
2. Build a wheel package for development. When developing locally, rather than building the library code into a wheel package with every code change, you can build and install the package for development.

```bash
cd src
python -m build
pip install --editable .
```

3. From the project root, run `pytest test/unittests`, or run tests in VSCode. <!-- markdownlint-disable MD029 -->

### Run integration tests

1. In a bash shell, set the environment variables defined in .env by running `export $(cat .env | xargs)`
1. Run [run_notebook_tests.sh](test/run_notebook_tests.sh). This will build and install library code as a wheel package and run the notebook as one-time job run.

## How to run GitHub CI/CD workflow

The GitHub workflow runs on [push or pull request to the main branch](.github/workflows/cicd.yml#L4).

1. In GitHub repo __Settings__, create a environment `Databricks_Azure_Test`, and configure 3 environment secrets: `DATABRICKS_CLUSTERID`, `DATABRICKS_HOST`, and `DATABRICKS_TOKEN`. These are used for Databricks Connect to run the unit tests.
1. Create another environment `Databricks_Azure_Production`, and configure 2 environment secrets: `DATABRICKS_HOST` and `DATABRICKS_TOKEN`. These are used to deploy Databricks jobs.
1. Optionally add a reviewer for the `Databricks_Azure_Production` environment, so that the workflow will wait for a reviewer to approve the deployment.
