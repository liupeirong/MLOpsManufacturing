from azureml.core import Workspace
from ml_service.util.env_variables import Env


if __name__ == "__main__":
    # Environment variables
    env = Env()

    ws = Workspace.create(name=env.aml_workspace_name,
                          subscription_id=env.subscription_id,
                          resource_group=env.resource_group,
                          create_resource_group=True,
                          location=env.aml_workspace_location,
                          exist_ok=True)

    # .azureml/config.json file will be created.
    ws.write_config()
