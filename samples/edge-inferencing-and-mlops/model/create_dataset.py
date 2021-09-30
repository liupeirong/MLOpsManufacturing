import argparse
import pandas as pd
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split

# Dataset creation params
n_samples = 1000
centers = 2
cluster_std = 4.0
random_state_ds_creation = 42

# Training and Tests split params
test_size = 0.25
random_state_train_test_split = 42

training_df_file_name = "training_data.csv"
test_df_file_name = "test_data.csv"


def get_args():
    parser = argparse.ArgumentParser(description='Process arguments')

    parser.add_argument('--output-folder', type=str, dest='output_folder',
                        default='./dataset', help='Output folder')

    args = parser.parse_args()

    return args


def create_dataframe(X, y) -> pd.DataFrame:
    df = pd.DataFrame({
        "x1": X[:, 0],
        "x2": X[:, 1],
        "y": y
    })

    return df


def main():
    args = get_args()
    training_df_output_path = f"{args.output_folder}/{training_df_file_name}"
    test_df_output_path = f"{args.output_folder}/{test_df_file_name}"

    X, y_true = make_blobs(
        n_samples=n_samples,
        centers=centers,
        cluster_std=cluster_std,
        random_state=random_state_ds_creation
    )

    X = X[:, ::-1]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_true,
        test_size=test_size,
        random_state=random_state_train_test_split
    )

    training_df = create_dataframe(X_train, y_train)
    test_df = create_dataframe(X_test, y_test)

    training_df.to_csv(training_df_output_path, index=False)
    test_df.to_csv(test_df_output_path, index=False)


if __name__ == "__main__":
    main()
