from azureml.core import Workspace, Experiment, Environment, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies

"""
$ python -m ml_service.run_local_compute
"""

ws = Workspace.from_config()

environment = Environment(name='mylocal_env')
environment.python.user_managed_dependencies = True
environment.python.conda_dependencies = CondaDependencies(conda_dependencies_file_path="./environment_setup/conda_dependencies.yml")

config = ScriptRunConfig(source_directory='src/steps',
                         script='01_prep_data.py',
                         compute_target='local',  # or 'cpu-cluster'
                         arguments=[
                                '--data_X', 'outputs/diabetes_X2.csv',
                                '--data_y', 'outputs/diabetes_y2.csv'
                         ],
                         environment=environment)

exp = Experiment(workspace=ws, name='mylocal_exp')
run = exp.submit(config)

aml_url = run.get_portal_url()
print(aml_url)
