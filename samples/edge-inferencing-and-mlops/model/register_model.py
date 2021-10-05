import os
import argparse
from azureml.core import Run, Model
from shutil import copy2
import sklearn


def parse_args():
    parser = argparse.ArgumentParser(description='Process arguments')

    parser.add_argument('--data-folder', type=str, dest='data_folder',
                        default=None, help='Dataset folder')
    parser.add_argument('--model-name', type=str, dest='model_name',
                        default='simple_classifier', help='Model name')
    parser.add_argument('--build-id', type=str, dest='build_id',
                        default=None, help='Build Id')
    parser.add_argument('--build-source', type=str, dest='build_source',
                        default=None, help='Build Source')

    args = parser.parse_args()

    return args


def copy_req_model_files(data_path, model_path):
    copy2(os.path.join(data_path, "classifier.pkl"), model_path)


def main():
    print('Run register model')

    args = parse_args()

    # Get the experiment run context
    run = Run.get_context()

    # Define data folder
    data_path = run.input_datasets['input_dataset'] if args.data_folder is None else args.data_folder
    print(f'Use data_path: {data_path}')

    # Determine if it is offline run
    is_offline_run = run.id.startswith('OfflineRun')

    # Make dir for model_path
    model_path = args.model_name if not is_offline_run else os.path.join('final_model_output', args.model_name)
    os.makedirs(model_path, exist_ok=True)
    print(f'Use model_path: {model_path}')

    # Copy required model files
    print('Copy required model files')
    copy_req_model_files(data_path, model_path)

    if not is_offline_run:
        # Get model properties
        print('Get model properties')
        model_properties = run.parent.get_properties()
        model_properties['build_id'] = args.build_id
        model_properties['build_source'] = args.build_source
        print(f'Model properties: {model_properties}')

        # Upload model files
        print('Upload model files')
        run.upload_folder(
            name=args.model_name,
            path=model_path)

        # Register model
        print('Register model')
        run.register_model(
            model_name=args.model_name,
            model_path=model_path,
            model_framework=Model.Framework.SCIKITLEARN,
            model_framework_version=sklearn.__version__,
            properties=model_properties
        )

    else:
        print('Offline run: Skipped registering model')

    print('Completed register model')


if __name__ == '__main__':
    main()
