from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from ml_service.util.env_variables import Env


if __name__ == "__main__":
    # Environment variables
    env = Env()

    ws = Workspace.from_config()  # Load config from .azureml

    # Choose a name for your CPU cluster
    cpu_cluster_name = env.aml_compute_name

    # Verify that the cluster does not exist already
    try:
        cpu_cluster = AmlCompute(workspace=ws, name=cpu_cluster_name)
        print('Found existing cluster, use it.')
    except ComputeTargetException:
        compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
                                                               idle_seconds_before_scaledown=2400,
                                                               min_nodes=0,
                                                               max_nodes=4)
        cpu_cluster = ComputeTarget.create(ws, cpu_cluster_name, compute_config)

    cpu_cluster.wait_for_completion(show_output=True)
