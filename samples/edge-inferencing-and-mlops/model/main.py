from azureml.core import Run
import pickle
import argparse
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score

from dataloader import DataLoader

# model params
C = 0.025
kernel = "linear"

# cross validation params
cv = 5


def get_args():
    parser = argparse.ArgumentParser(description='Process arguments')

    parser.add_argument('--data-folder', type=str, dest='data_folder',
                        default='./dataset', help='Output folder')

    parser.add_argument('--output-folder', type=str, dest='output_folder',
                        default='./output_model', help='Output folder')

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    run = Run.get_context()
    is_offline_run = run.id.startswith('OfflineRun')
    print(f"Is Offline Run: {is_offline_run}")
    if is_offline_run:
        dataloader = DataLoader(args.data_folder)
        X_train, y_train = dataloader.load_training_data()
        X_test, y_test = dataloader.load_test_data()
    else:
        training_data = run.input_datasets['training_dataset']
        test_dataset = run.input_datasets['test_dataset']

        training_df = training_data.to_pandas_dataframe()
        test_df = test_dataset.to_pandas_dataframe()

        training_df = training_df.drop(['Path'], axis=1)
        test_df = test_df.drop(['Path'], axis=1)

        X_train, y_train = training_df.iloc[:, :-1].values, training_df.iloc[:, -1].values
        X_test, y_test = test_df.iloc[:, :-1].values, test_df.iloc[:, -1].values

    clf = svm.SVC(kernel=kernel, C=C)
    scores = cross_val_score(clf, X_train, y_train, cv=cv)

    print(f"Cross validation scores: {scores};")

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_pred, y_test)

    print(f"Accuracy: {accuracy}")

    model_output = f"{args.output_folder}/classifier.pkl"
    pickle.dump(clf, open(model_output, 'wb'))


if __name__ == "__main__":
    main()
