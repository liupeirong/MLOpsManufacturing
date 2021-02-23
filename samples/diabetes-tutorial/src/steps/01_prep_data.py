from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace
from sklearn.datasets import load_diabetes
import numpy as np
import argparse
import os

"""
$ python -m src.steps.01_prep_data \
    --data_X=outputs/diabetes_X.csv \
    --data_y=outputs/diabetes_y.csv
"""

# Get context
run = Run.get_context()
ws = Workspace.from_config() if type(run) == _OfflineRun else run.experiment.workspace

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_X', type=str)
    parser.add_argument('--data_y', type=str)
    args = parser.parse_args()
    print(f'--data_X={args.data_X}')
    print(f'--data_y={args.data_y}')

    # Load the diabetes dataset
    diabetes_X, diabetes_y = load_diabetes(return_X_y=True)

    # Use only one feature
    diabetes_X = diabetes_X[:, np.newaxis, 2]

    # save data_X
    data_X_path = args.data_X
    os.makedirs(os.path.dirname(data_X_path), exist_ok=True)
    np.savetxt(data_X_path, diabetes_X, delimiter=',')
    print(f'Exported to {data_X_path} {diabetes_X.shape}')

    # save data_y
    data_y_path = args.data_y
    os.makedirs(os.path.dirname(data_y_path), exist_ok=True)
    np.savetxt(data_y_path, diabetes_y, delimiter=',')
    print(f'Exported to {data_y_path} {diabetes_y.shape}')
