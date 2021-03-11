from azureml.core import Workspace, Environment, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.environment import DEFAULT_CPU_IMAGE
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core.graph import TrainingOutput
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.steps import HyperDriveStep
from azureml.pipeline.core import Pipeline, PipelineData, PipelineParameter, PipelineEndpoint
from azureml.pipeline.core._restclients.aeva.models.error_response import ErrorResponseException
from ml_service.util.env_variables import Env
from ml_service.pipelines.hyperparams import HyperParams


"""
$ python -m ml_service.pipelines.build_pipeline && python -m ml_service.pipelines.run_pipeline --test_size=0.2
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

    # ===== hyper drive setup //
    config = ScriptRunConfig(source_directory='src/steps',
                             script='02_train.py',
                             compute_target=env.aml_compute_name,
                             arguments=[
                                 '--data_X', data_X,
                                 '--data_y', data_y,
                                 '--model_name', env.aml_model_name,
                                 '--test_size', pipeparam_test_size
                             ],
                             environment=environment)

    hd_config = HyperParams().get_hd_config(config)

    metrics_output_name = 'metrics_output'
    metrics_data = PipelineData(name='metrics_data',
                                datastore=ds,
                                pipeline_output_name=metrics_output_name)

    best_model_output_name = 'best_model_output'
    saved_model = PipelineData(name='saved_model',
                               datastore=ds,
                               pipeline_output_name=best_model_output_name,
                               training_output=TrainingOutput("Model", model_file="outputs/mymodel"))

    step2 = HyperDriveStep(
        name='tune hyperparams',
        hyperdrive_config=hd_config,
        inputs=[data_X, data_y],
        outputs=[saved_model],
        metrics_output=metrics_data)
    # ===== // hyper drive setup

    step3 = PythonScriptStep(
        name="register model",
        compute_target=env.aml_compute_name,
        source_directory='src/steps',
        script_name='03_reg_model.py',
        inputs=[saved_model, metrics_data],
        outputs=[],
        arguments=[
            '--model_name', env.aml_model_name,
            '--saved_model', saved_model,
            '--metrics_data', metrics_data
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
