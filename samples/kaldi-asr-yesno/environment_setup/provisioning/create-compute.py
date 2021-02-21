from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from ml_service.util.env_variables import Env

# Environment variables
env = Env()

# Azure ML workspace
aml_workspace = Workspace.get(
    name=env.workspace_name,
    subscription_id=env.subscription_id,
    resource_group=env.resource_group,
)

# Verify that the cluster does not exist already
try:
    cpu_cluster = ComputeTarget(workspace=aml_workspace, name=env.compute_name)
    print('Found existing cluster, use it.')
except ComputeTargetException:
    compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                           idle_seconds_before_scaledown=2400,
                                                           min_nodes=0,
                                                           max_nodes=1)
    cpu_cluster = ComputeTarget.create(aml_workspace, env.compute_name, compute_config)

cpu_cluster.wait_for_completion(show_output=True)
