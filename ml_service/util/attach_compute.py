
from azureml.core import Workspace
from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException
from ml_service.util.env_variables import Env
from ml_service.util.logger.observability import observability


def get_compute(workspace: Workspace, compute_name: str, vm_size: str):  # NOQA E501
    try:
        if compute_name in workspace.compute_targets:
            compute_target = workspace.compute_targets[compute_name]
            if compute_target and type(compute_target) is AmlCompute:
                observability.log("Found existing compute target " + compute_name + " so using it.") # NOQA
        else:
            e = Env()
            compute_config = AmlCompute.provisioning_configuration(
                vm_size=vm_size,
                vm_priority=e.vm_priority,
                min_nodes=e.min_nodes,
                max_nodes=e.max_nodes,
                idle_seconds_before_scaledown="300"
                #    #Uncomment the below lines for VNet support
                #    vnet_resourcegroup_name=vnet_resourcegroup_name,
                #    vnet_name=vnet_name,
                #    subnet_name=subnet_name
            )
            compute_target = ComputeTarget.create(
                workspace, compute_name, compute_config
            )
            compute_target.wait_for_completion(
                show_output=True, min_node_count=None, timeout_in_minutes=10
            )
        return compute_target
    except ComputeTargetException as ex:
        observability.exception(ex)
        print("An error occurred trying to provision compute.")
        exit(1)
