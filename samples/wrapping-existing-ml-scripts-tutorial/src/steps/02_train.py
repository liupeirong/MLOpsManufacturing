from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import os
import joblib
import numpy as np
import matplotlib.pyplot as plt
import argparse

"""
$ python -m src.steps.02_train \
    --data_X=outputs/diabetes_X.csv \
    --data_y=outputs/diabetes_y.csv \
    --model_dir=outputs \
    --model_name=model.pkl \
    --test_size=0.2
"""

# Get context
run = Run.get_context()
ws = Workspace.from_config() if type(run) == _OfflineRun else run.experiment.workspace

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_X', type=str)
    parser.add_argument('--data_y', type=str)
    parser.add_argument('--model_dir', type=str)
    parser.add_argument('--model_name', type=str)
    parser.add_argument('--test_size', type=float, default=0.2)
    args = parser.parse_args()
    print(f'--data_X={args.data_X}')
    print(f'--data_y={args.data_y}')
    print(f'--model_dir={args.model_dir}')
    print(f'--model_name={args.model_name}')
    print(f'--test_size={args.test_size}')

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
    model = LinearRegression()
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

    # image log
    plt.scatter(X_test, y_test, color='black')
    plt.plot(X_test, y_pred, color='blue', linewidth=3)
    plt.xticks(())
    plt.yticks(())
    plt.show()
    plt.savefig('outputs/fig.png')
    run.log_image("ROC", plot=plt)

    # Save the model file
    model_file = os.path.join(args.model_dir, args.model_name)
    os.makedirs(os.path.dirname(model_file), exist_ok=True)
    joblib.dump(value=model, filename=model_file)
    print(f'Saved model file to {model_file}')

    # NOTE: If the file saves in the "outputs" directory, it will be automatically uploaded into output+log section of experiment.
    # Save the model to outputs for history
    model_file = os.path.join('outputs', args.model_name)
    os.makedirs(os.path.dirname(model_file), exist_ok=True)
    joblib.dump(value=model, filename=model_file)
    print(f'Saved model file to {model_file}')
