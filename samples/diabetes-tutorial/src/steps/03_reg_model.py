from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace, Model
import argparse

"""
$ python -m src.steps.03_reg_model \
    --model_dir=outputs \
    --model_name=model.pkl
"""

# Get context
run = Run.get_context()
ws = Workspace.from_config() if type(run) == _OfflineRun else run.experiment.workspace

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_dir', type=str)
    parser.add_argument('--model_name', type=str)
    args = parser.parse_args()
    print(f'--model_dir={args.model_dir}')
    print(f'--model_name={args.model_name}')

    # Register model
    model = Model.register(workspace=ws,
                           model_path=args.model_dir,
                           model_name=args.model_name)
    print(model)
