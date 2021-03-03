# Overview

This sample guides you how to transform your existing machine learning code to work efficiently with Azure Machine Learning Service Pipelines.

## Introduction

Our fictive scenario will use a simple diabetes linear regression code based on Scikit-learn.

> Linear Regression Example: https://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html

Questions:

- What needs to be done to run the regression on Azure Machine Learning?
- What do we need to do to leverage MLOps features of Azure Machine Learning?

We will guide you step by step through both answers to these questions. 

# Getting Started

## Prerequisite
- Install Visual Studio Code: https://code.visualstudio.com
- Install Docker: https://www.docker.com
- Register Azure account: https://azure.microsoft.com/free

## Step 0. Setup dev environment

- clone this repo
- Open vscode in dev container
  
  > The first run can take a long time because it builds docker images.

  Then open the terminal and do the following:

- Install the Azure CLI - [read more...](https://docs.microsoft.com/cli/azure/install-azure-cli-linux?pivots=apt)
  
  ```bash
  $ curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
  ```
  
- Sign in to Azure with the Azure CLI - [read more...](https://docs.microsoft.com/cli/azure/install-azure-cli-linux?pivots=apt#sign-in-to-azure-with-the-azure-cli)

  ```bash
  $ az login
  ```

  > If you have multiple subscriptions, check and set your subscriptions id.
  > ```bash
  > $ az account list -o table
  > $ az account set -s [Your subscription Id]
  > ```

- Install Conda dependencies

  > If you want to print the conda env name at the prompt...
  > ```bash
  > $ conda init zsh && zsh 
  > ```
  ```bash
  $ conda env create --file environment_setup/conda_dependencies.yml
  $ conda activate my_conda
  ```

- Create Azure ML workspace with Python - [read more...](https://docs.microsoft.com/azure/machine-learning/how-to-manage-workspace?tabs=python#create-a-workspace)

  ```bash
  # Rename /.env.example to /.env
  # Set your SUBSCRIPTION_ID in the file
  $ python -m environment_setup.provisioning.create_workspace
  ```
  > Created in about 30 seconds.

- Create Compute cluster with Python

  ```bash
  $ python -m environment_setup.provisioning.create_compute
  ```

- Let's go check out your Azure ML workspace!

  Go to https://ml.azure.com/ or you can access through https://portal.azure.com.

  ![AML Portal](docs/image-20210218233512072.png)

  Check your compute cluster
  
  ![Compute cluster](docs/image-20210218233745354.png)


## Step 1. Run your train.py

As mentioned earlier, you have a simple diabetes Linear regression code using Scikit-learn. First, let's check if this code works properly in your local environment.

```bash
$ python -m src.train
Mean squared error:  4150.680189329983
Coefficient of determination:  0.19057346847560164
```

When finished, you should see the metrics, the *sklearn_regression_model.pkl* file and *fig.png* graph image in the *outputs* folder.


## Step 2. Split your train.py into steps

From now on, the long journey to make your code ready for MLOps begins. The first action is to split your code. Your code works well on your dev environment with single file, but you should fragment it for an optimal MLOps implementation.

![split your code](docs/image-20210219000056606.png)

It's up to you to decide how detailed you want to split! But for now... let's break down into 3 steps: Data Preparation, Train, Register Model. The resulting scripts are already preprepared in the *src/steps* folder.

- *src/steps/01_prep_data.py*

  > Gets the diabetes data, makes it as X, y, and places only one feature in X.

- *src/steps/02_train.py*

  > Perform the training, print the results (mse, r2score, matplot image) and generate the model.

- *src/steps/03_reg_model.py*

  > Register the model file with Azure ML workspace.

> The most effort for the adaption is to handle parameters with *argparse* and do logging via *Run.get_context()*. Of course, there is additional work to do if you want to use advanced features!

So, now you can test if the scripts are running in your local environment.

```bash
$ python -m src.steps.01_prep_data \
    --data_X=outputs/diabetes_X.csv \
    --data_y=outputs/diabetes_y.csv
$ python -m src.steps.02_train \
    --data_X=outputs/diabetes_X.csv \
    --data_y=outputs/diabetes_y.csv \
    --model_dir=outputs \
    --model_name=model.pkl \
    --test_size=0.2
$ python -m src.steps.03_reg_model \
    --model_dir=outputs \
    --model_name=model.pkl
```

If the csv files, graph file, and pkl file are all created in the outputs folder, everything completed successfully!

## Step 3. Run steps with AML

Now let's make sure this code works in Azure. Before setting up the MLOps pipeline, we can test if your code executes within Azure ML.

```bash
$ python -m ml_service.run_local_compute
```

The above command will execute the *src/steps/01_prep_data.py* file through the AML Workspace. This can be used if you just want to run a single python file in AML, where you don't need a MLOps pipeline.

```python
...
config = ScriptRunConfig(source_directory='src/steps',
                         script='01_prep_data.py',
                         compute_target='local',  # or 'cpu-cluster'
                         arguments=[
                                '--data_X', 'outputs/diabetes_X2.csv',
                                '--data_y', 'outputs/diabetes_y2.csv'
                         ],
                         environment=environment)
...
```

This code sets `compute_target='local'`  so the compute uses your local computer.

> The result files such as *'outputs/diabetes_X2.csv* and *'outputs/diabetes_y2.csv* will remain in the */tmp/azuremk_runs* folder of your local computer.

> If you set `compute_target='cpu-cluster'`, it will run on the compute cluster you created above. The first run requires time to be provisioned. (You will be charged as much as the running time!)

This process can be repeated for each step script, in order to check if it works well together with Azure ML.

## Step 4. Creating the MLOps pipeline

Now it's time to create a pipeline. Let's have a look at the code */ml_service/pipelines/build_pipeline.py*. This script builds the AML pipeline.

```python
...
    environment = Environment(name=env.aml_environment_name)
    environment.docker.enabled = True
    environment.docker.base_image = DEFAULT_CPU_IMAGE
    environment.python.user_managed_dependencies = False
    environment.python.conda_dependencies = CondaDependencies(conda_dependencies_file_path="./environment_setup/conda_dependencies.yml")
...
```

The above code defines the environment in which each pipeline step runs. This is where you configure your custom conda environment using the built-in CPU Docker Image. You can also use custom docker images from *Azure Container Registry* or *Docker Hub*.

```python
...
    # Create Pipeline data & parameters
    ds = ws.get_default_datastore()
    data_X = PipelineData('data_X', datastore=ds).as_dataset()
    data_y = PipelineData('data_y', datastore=ds).as_dataset()
    model_dir = PipelineData('model_dir', datastore=ds)
    pipeparam_test_size = PipelineParameter(name="pipeparam_test_size", default_value=0.2)
...
```

The above code creates *PipelineData* objects which help transfer the input and result data between Pipeline Steps. And *PipelineParameter* can pass additional parameters whenever you run the pipeline.



Next, create each step.

```python
...
step2 = PythonScriptStep(
        name="train",
        compute_target=env.aml_compute_name,
        source_directory='src/steps',
        script_name='02_train.py',
        inputs=[data_X, data_y],
        outputs=[model_dir],
        arguments=[
            '--data_X', data_X,
            '--data_y', data_y,
            '--model_dir', model_dir,
            '--model_name', env.aml_model_name,
            '--test_size', pipeparam_test_size
        ],
        runconfig=run_config,
        allow_reuse=False
    )
...
```

> Isn't it similar to the ml_service/run_local_compute.py file above? *PipelineStep* can be connected to each step, but *ScriptRunConfig* can only run a single file. In addition, *PipelineStep* cannot use `compute_targert='local'`, this is only possible to use in *ScriptRunConfig*. 
>
> Therefore, going to *PipelineStep* after working enough with *ScriptRunConfig* in your local environment saves time and money!

Because each step is connected by *inputs* and *outputs*, all steps are automatically added to the pipeline even if only one of the steps is added.

```python
...
	# Build pipeline
    pipeline = Pipeline(workspace=ws, steps=[step3])
    pipeline.validate()
...
```

Publish your pipeline and add a *PipelineEndpoint* to it.

```python
...
# Publish pipeline & pipeline_endpoint
    published_pipeline = pipeline.publish(name=env.aml_pipeline_name)

    try:
        pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name=env.aml_pipeline_endpoint_name)
        pipeline_endpoint.add_default(published_pipeline)
    except ErrorResponseException:
        pipeline_endpoint = PipelineEndpoint.publish(workspace=ws, name=env.aml_pipeline_endpoint_name, description=env.aml_pipeline_endpoint_name, pipeline=published_pipeline)
...
```

> *PipelineEndpoint* is an object that integrates multiple pipelines.  Allows you to manage the version of the pipelines and call the latest version of the pipeline with a single REST API address.

Now let's build the pipeline.

```bash
$ python -m ml_service.pipelines.build_pipeline
```

Go to the Azure ML workspace portal to see that the pipeline has been created.

![pipeline](docs/image-20210219011443262.png)



## Step 5. Run MLOps pipeline

Last but not least, let's run the published pipeline.

```bash
$ python -m ml_service.pipelines.run_pipeline --test_size=0.2
```

You can pass parameters when you run the pipeline. When you execute the code above, you get a link to the Azure ML Workspace and go to the link to see the progress of the pipeline.

> Provisioning might take some time if the cpu-cluster is not provisioned!

You can see that each step is running:

![pipeline success](docs/image-20210219011557547.png)

You can view the log results at each step.

![metrics](docs/image-20210219011645541.png)

You can get the latest model.

![model](docs/image-20210219011737443.png)


# Conclusion

We introduced a basic process pattern on how to move your existing Machine Learning code to be executed by an Azure ML Pipeline.
Now it's time to make your own MLOps according to your needs. Good luck!


# References

- https://azure.github.io/azureml-examples/
- https://docs.microsoft.com/azure/machine-learning/how-to-create-machine-learning-pipelines
- https://github.com/microsoft/MLOpsPython
- https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-getting-started.ipynb
