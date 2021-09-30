import argparse
import utils.settings as env
from datetime import datetime
from azureml.core import Dataset, Datastore
from azureml.datadrift import DataDriftDetector
from msrest.exceptions import HttpOperationError
from utils.workspace import get_workspace

baseline_day = datetime(2020, 11, 2)
# Variable to choose the correct index for splitting the path name
line_index = 3

# Maximum batch size is 30 days
# Make sure that these are within 30 days of each other
backfill_start_date = datetime(2021, 8, 22)
backfill_end_date = datetime.now()

# Update this feature list with the columns/feature of your sample data
features_list = []


def parse_args():
    parser = argparse.ArgumentParser(description='Process arguments')

    parser.add_argument('-d', '--debug-mode', type=bool, dest='debug_mode',
                        default=False, help='Run script in debug mode - data is csv instead of parquet')
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    # Get workspace configs - local function
    workspace, compute_target, datastore = get_configs(
        workspace_name=env.workspace_name,
        resource_group=env.workspace_resource_group,
        subscription_id=env.subscription_id,
        tenant_id=env.tenant_id,
        app_id=env.app_id,
        app_secret=env.app_secret,
        compute_target_name=env.compute_target_name,
        datastore_name=env.datastore_name,
        data_storage_account_name=env.data_storage_account_name,
        datastore_container_name=env.datastore_container_name,
        data_storage_account_key=env.data_storage_account_key
    )

    # This makes sure the backfill can run
    # in case the image build compute isn't updated from the terraform script
    workspace.update(image_build_compute=env.workspace_name)

    # Grab target + baseline path
    target_path = env.drift_target_path
    baseline_path = env.drift_baseline_path
    line = target_path.split('/')[line_index]

    baseline_dset, target_dset = create_datasets(workspace, datastore, target_path, baseline_path, line, args)

    monitor = create_data_monitor(
        workspace, features_list, compute_target, baseline_dset, target_dset, line, datastore.name
    )

    print('Running backfill from {0} to {1}...'.format(backfill_start_date, backfill_end_date))
    print('This will take anwyhere from 3-10 mins depending on the size of the dates for backfill')
    backfill = monitor.backfill(backfill_start_date, backfill_end_date)
    backfill.wait_for_completion(wait_post_processing=True)

    print('Backfill completed. Here are the results:')
    drift_metrics = backfill.get_metrics()

    for metric in drift_metrics:
        print(metric, drift_metrics[metric])
    monitor = monitor.enable_schedule()


def create_datasets(workspace, datastore, target_path, baseline_path, line, args):
    # get correct tag name
    tag_format = 'Parquet'
    if args.debug_mode:
        tag_format = 'CSV'

    target_name = '{0}-{1}-target'.format(datastore.name, line)
    baseline_name = '{0}-{1}-baseline'.format(datastore.name, line)

    print('Creating and registering target dataset...')
    if args.debug_mode:
        target_dset = Dataset.Tabular.from_delimited_files(path=(datastore, target_path))
    else:
        target_dset = Dataset.Tabular.from_parquet_files(path=(datastore, target_path))
    target_dset = target_dset.with_timestamp_columns('_time')
    target_dset = target_dset.register(workspace=workspace,
                                       name=target_name,
                                       description='target data for line {}'.format(line),
                                       tags={'format': tag_format},
                                       create_new_version=False)

    print('Target dataset registered')

    if baseline_path == '' or baseline_path is None:
        print('No path given for baseline. Creating + Registering baseline dataset based on target dataset...')
        baseline_dset = target_dset.time_before(baseline_day)
        # baseline_dset = target_dset.time_between(baseline_start, baseline_end, include_boundary)
        baseline_dset = baseline_dset.register(workspace, baseline_name, create_new_version=True)
    else:
        print('Creating baseline dataset based on path...')
        if args.debug_mode:
            baseline_dset = Dataset.Tabular.from_delimited_files(path=(datastore, baseline_path))
        else:
            baseline_dset = Dataset.Tabular.from_parquet_files(path=(datastore, baseline_path))
        baseline_dset = baseline_dset.register(workspace=workspace,
                                               name=baseline_name,
                                               description='baseline data for line {}'.format(line),
                                               tags={'format': tag_format},
                                               create_new_version=False)

    print('Baseline dataset registered')

    return baseline_dset, target_dset


def create_data_monitor(
        workspace,
        features_list,
        compute_target,
        baseline_dset,
        target_dset,
        line,
        datastore_name
):
    monitor_name = '{0}-{1}-monitor'.format(datastore_name, line)

    try:
        monitor = DataDriftDetector.get_by_name(workspace, monitor_name)
        print('Found monitor with name: {}'.format(monitor_name))
    except (Exception):
        print('Could not find drift detector. Making a new one...')
        monitor = DataDriftDetector.create_from_datasets(
                workspace,
                monitor_name,
                baseline_dset,
                target_dset,
                compute_target=compute_target,
                frequency='Day',
                feature_list=features_list,
                drift_threshold=.25,
                latency=24
        )
        print('Created monitor with name: {}'.format(monitor_name))

    monitor = monitor.update(feature_list=features_list)
    return monitor


def get_configs(
        workspace_name,
        resource_group,
        subscription_id,
        tenant_id,
        app_id,
        app_secret,
        compute_target_name,
        datastore_name,
        data_storage_account_name,
        datastore_container_name,
        data_storage_account_key
):
    # Use get_workspace from workspace.py
    workspace = get_workspace(
        workspace_name,
        resource_group,
        subscription_id,
        tenant_id,
        app_id,
        app_secret
    )

    compute_target = workspace.compute_targets[env.compute_target_name]

    try:
        datastore = Datastore.get(workspace, datastore_name)
        print('Found Blob Datastore with name: {}'.format(datastore_name))
    except HttpOperationError:
        print('Datastore does not exist. Creating a new one...')
        datastore = Datastore.register_azure_blob_container(
            workspace=workspace,
            datastore_name=datastore_name,
            account_name=data_storage_account_name,
            container_name=datastore_container_name,
            account_key=data_storage_account_key,
            subscription_id=subscription_id,
            resource_group=resource_group)
        print('Registered blob datastore with name: {}'.format(datastore_name))

    return workspace, compute_target, datastore


if __name__ == '__main__':
    main()
