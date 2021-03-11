from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace, Model
import joblib
import argparse

# Get context
run = Run.get_context()
ws = Workspace.from_config() if type(run) == _OfflineRun else run.experiment.workspace

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str)
    parser.add_argument('--metrics_data', type=str)
    parser.add_argument('--saved_model', type=str)
    args = parser.parse_args()
    print(f'--model_name={args.model_name}')
    print(f'--metrics_data={args.metrics_data}')
    print(f'--saved_model={args.saved_model}')

    # load model
    loaded_model = joblib.load(args.saved_model)
    print(loaded_model)

    # Register model
    model = Model.register(workspace=ws,
                           model_path=args.saved_model,
                           model_name=args.model_name)
    print(model)
