
from azureml.core import Workspace, Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.environment import DEFAULT_CPU_IMAGE
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData, PipelineParameter, PipelineEndpoint
from azureml.pipeline.core._restclients.aeva.models.error_response import ErrorResponseException
from ml_service.util.env_variables import Env

"""
$ python -m ml_service.pipelines.build_pipeline
"""

if __name__ == "__main__":
    # Environment variables
    env = Env()

    # Setup run config
    ws = Workspace.from_config()

    environment = Environment(name=env.aml_environment_name)
    environment.docker.enabled = True
    environment.docker.base_image = DEFAULT_CPU_IMAGE
    environment.python.user_managed_dependencies = False
    environment.python.conda_dependencies = CondaDependencies(conda_dependencies_file_path="./environment_setup/conda_dependencies.yml")

    run_config = RunConfiguration()
    run_config.environment = environment

    # Create Pipeline data & parameters
    ds = ws.get_default_datastore()
    data_X = PipelineData('data_X', datastore=ds).as_dataset()
    data_y = PipelineData('data_y', datastore=ds).as_dataset()
    model_dir = PipelineData('model_dir', datastore=ds)
    pipeparam_test_size = PipelineParameter(name="pipeparam_test_size", default_value=0.2)

    # Create Pipeline steps
    step1 = PythonScriptStep(
        name="prep data",
        compute_target=env.aml_compute_name,
        source_directory='src/steps',
        script_name='01_prep_data.py',
        inputs=[],
        outputs=[data_X, data_y],
        arguments=[
            '--data_X', data_X,
            '--data_y', data_y
        ],
        runconfig=run_config,
        allow_reuse=True
    )

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

    step3 = PythonScriptStep(
        name="register model",
        compute_target=env.aml_compute_name,
        source_directory='src/steps',
        script_name='03_reg_model.py',
        inputs=[model_dir],
        outputs=[],
        arguments=[
            '--model_dir', model_dir,
            '--model_name', env.aml_model_name
        ],
        runconfig=run_config,
        allow_reuse=False
    )

    # Build pipeline
    pipeline = Pipeline(workspace=ws, steps=[step3])
    pipeline.validate()

    # Publish pipeline & pipeline_endpoint
    published_pipeline = pipeline.publish(name=env.aml_pipeline_name)

    try:
        pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name=env.aml_pipeline_endpoint_name)
        pipeline_endpoint.add_default(published_pipeline)
    except ErrorResponseException:
        pipeline_endpoint = PipelineEndpoint.publish(workspace=ws, name=env.aml_pipeline_endpoint_name, description=env.aml_pipeline_endpoint_name, pipeline=published_pipeline)
