"""
Copyright (C) Microsoft Corporation. All rights reserved.​
"""
from azureml.core.run import Run
import argparse
import subprocess
from util.model_helper import get_or_register_dataset, get_aml_context


def main():
    print("Running preprocess_os_cmd.py")

    parser = argparse.ArgumentParser("preprocess_os_cmd")
    parser.add_argument(
        "--dataset_name",
        type=str,
        help=("Dataset name. Dataset must be passed by name\
              to always get the desired dataset version\
              rather than the one used while the pipeline creation")
    )

    parser.add_argument(
        "--datastore_name",
        type=str,
        help=("Datastore name. If none, use the default datastore")
    )

    parser.add_argument(
        "--data_file_path",
        type=str,
        help=("data file path, if specified,\
               a new version of the dataset will be registered")
    )

    parser.add_argument(
        "--output_dataset",
        type=str,
        help=("output for passing data to next step")
    )

    args = parser.parse_args()

    print("Argument [dataset_name]: %s" % args.dataset_name)
    print("Argument [datastore_name]: %s" % args.datastore_name)
    print("Argument [data_file_path]: %s" % args.data_file_path)
    print("Argument [output_dataset]: %s" % args.output_dataset)

    data_file_path = args.data_file_path
    dataset_name = args.dataset_name
    datastore_name = args.datastore_name
    output_dataset_path = args.output_dataset

    run = Run.get_context()

    # Get Azure machine learning workspace
    aml_workspace, *_ = get_aml_context(run)

    # Get the dataset
    dataset = get_or_register_dataset(
        dataset_name,
        datastore_name,
        data_file_path,
        aml_workspace)

    # Link dataset to the step run so it is trackable in the UI
    run.input_datasets['input_dataset'] = dataset

    # Process data
    mount_context = dataset.mount()
    mount_context.start()
    print(f"mount_point is: {mount_context.mount_point}")

    ####
    # Execute something here just 'cp' from input to output folder
    #   cp /tmp/. /tmp2 -r
    # Prepackage any command line tools needed,
    # in the docker image (ml_model/preprocessing/Dockerfile)
    process = subprocess.Popen(['cp',
                                '{0}/.'.format(mount_context.mount_point),
                                output_dataset_path,
                                '-r',
                                '-v'],
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
    # Check output
    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                print(output.strip())
            break

    mount_context.stop()

    run.tag("run_type", value="preprocess_os_cmd")
    print(f"tags now present for run: {run.tags}")

    run.complete()


if __name__ == '__main__':
    main()
