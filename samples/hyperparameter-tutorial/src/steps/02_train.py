from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import os
import joblib
import numpy as np
import argparse

# Get context
run = Run.get_context()
ws = Workspace.from_config() if type(run) == _OfflineRun else run.experiment.workspace

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_X', type=str)
    parser.add_argument('--data_y', type=str)
    parser.add_argument('--model_name', type=str)
    parser.add_argument('--test_size', type=float, default=0.2)
    parser.add_argument('--alpha', type=float, default=0.1)
    args = parser.parse_args()
    print(f'--data_X={args.data_X}')
    print(f'--data_y={args.data_y}')
    print(f'--model_name={args.model_name}')
    print(f'--test_size={args.test_size}')
    print(f'--alpha={args.alpha}')

    # read data
    data_X_path = args.data_X
    data_X = np.loadtxt(data_X_path, delimiter=',')
    data_X = data_X.reshape(-1, 1)
    print(f'Read from {data_X_path} {data_X.shape}')

    data_y_path = args.data_y
    data_y = np.loadtxt(data_y_path, delimiter=',')
    print(f'Read from {data_y_path} {data_y.shape}')

    # split data
    X_train, X_test, y_train, y_test = train_test_split(data_X, data_y, test_size=args.test_size, random_state=0)

    # train
    model = Ridge(alpha=args.alpha)
    model.fit(X_train, y_train)

    # predict
    y_pred = model.predict(X_test)
    run.log_list('y_pred', y_pred)

    # The mean squared error
    print('Mean squared error: ', mean_squared_error(y_test, y_pred))
    # The coefficient of determination: 1 is perfect prediction
    print('Coefficient of determination: ', r2_score(y_test, y_pred))
    run.log('mse', mean_squared_error(y_test, y_pred))
    run.log('r2', r2_score(y_test, y_pred))

    # Save the model to outputs
    model_file = os.path.join('outputs', args.model_name)
    os.makedirs(os.path.dirname(model_file), exist_ok=True)
    joblib.dump(value=model, filename=model_file)
    print(f'Saved model file to {model_file}')
