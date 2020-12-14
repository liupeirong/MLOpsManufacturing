"""
model_helper.py
"""
from azureml.core import Run
from azureml.core import Workspace, Dataset, Datastore
from azureml.core.model import Model as AMLModel


def get_aml_context(run):
    if (run.id.startswith('OfflineRun')):
        from azureml.core import Experiment
        from dotenv import load_dotenv
        import os
        load_dotenv()
        workspace_name = os.environ.get("WORKSPACE_NAME")
        experiment_name = os.environ.get("EXPERIMENT_NAME")
        resource_group = os.environ.get("RESOURCE_GROUP")
        subscription_id = os.environ.get("SUBSCRIPTION_ID")
        # run_id useful to query previous runs
        run_id = "bd184a18-2ac8-4951-8e78-e290bef3b012"
        ws = Workspace.get(
            name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group
        )
        exp = Experiment(ws, experiment_name)
    else:
        ws = run.experiment.workspace
        exp = run.experiment
        run_id = 'amlcompute'
    return ws, exp, run_id


def get_model(
    model_name: str,
    model_version: int = None,  # If none, return latest model
    tag_name: str = None,
    tag_value: str = None,
    aml_workspace: Workspace = None
) -> AMLModel:
    """
    Retrieves and returns a model from the workspace by its name
    and (optional) tag.

    Parameters:
    aml_workspace (Workspace): aml.core Workspace that the model lives.
    model_name (str): name of the model we are looking for
    (optional) model_version (str): model version. Latest if not provided.
    (optional) tag (str): the tag value & name the model was registered under.

    Return:
    A single aml model from the workspace that matches the name and tag, or
    None.
    """
    if aml_workspace is None:
        print("No workspace defined - using current experiment workspace.")
        aml_workspace, *_ = get_aml_context(Run.get_context(allow_offline=False))  # NOQA: E501

    tags = None
    if tag_name is not None or tag_value is not None:
        # Both a name and value must be specified to use tags.
        if tag_name is None or tag_value is None:
            raise ValueError("model_tag_name and model_tag_value should both be supplied or excluded")  # NOQA: E501
        tags = [[tag_name, tag_value]]

    model = None
    if model_version is not None:
        # TODO(tcare): Finding a specific version currently expects exceptions
        # to propagate in the case we can't find the model. This call may
        # result in a WebserviceException that may or may not be due to the
        # model not existing.
        model = AMLModel(
            aml_workspace,
            name=model_name,
            version=model_version,
            tags=tags)
    else:
        models = AMLModel.list(
            aml_workspace, name=model_name, tags=tags, latest=True)
        if len(models) == 1:
            model = models[0]
        elif len(models) > 1:
            raise Exception("Expected only one model")

    return model


def register_dataset(
    aml_workspace: Workspace,
    dataset_name: str,
    datastore_name: str,
    file_path: str
) -> Dataset:
    if datastore_name:
        datastore = Datastore.get(aml_workspace, datastore_name)
    else:
        datastore = aml_workspace.get_default_datastore()
    # if the path is same as the latest version, no new version will be registered  # NOQA: E501
    # however, run.input_datasets['name'] = dataset will not log the dataset in the run  # NOQA: E501
    # in this case, the dataset returned from Dataset.get_by_name does get logged  # NOQA: E501
    dataset = Dataset.File.from_files(path=(datastore, file_path))
    dataset = dataset.register(workspace=aml_workspace,
                               name=dataset_name,
                               create_new_version=True)

    return Dataset.get_by_name(aml_workspace, dataset_name)


def get_or_register_dataset(
    dataset_name: str,
    datastore_name: str,
    data_file_path: str,
    aml_workspace: Workspace = None
) -> Dataset:
    if dataset_name is None:
        raise Exception("Datset name can't be null")

    if aml_workspace is None:
        print("No workspace defined - using current experiment workspace.")
        aml_workspace, *_ = get_aml_context(Run.get_context())

    if data_file_path == "nopath":
        print(f"get latest version of dataset: {dataset_name}")
        dataset = Dataset.get_by_name(aml_workspace, dataset_name)
    else:
        print(f"register a new dataset or new version: {dataset_name}, {datastore_name}, {data_file_path}")  # NOQA: E501
        dataset = register_dataset(
            aml_workspace,
            dataset_name,
            datastore_name,
            data_file_path)

    return dataset
