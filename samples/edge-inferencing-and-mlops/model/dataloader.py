import os
import pandas as pd


class DataLoader:
    def __init__(self, data_folder: str):
        self.training_dataset_path = f"{data_folder}/training_data.csv"
        self.test_dataset_path = f"{data_folder}/test_data.csv"

    def load_training_data(self) -> tuple:
        if not os.path.exists(self.training_dataset_path):
            raise IOError(f"Path does not exist: {self.training_dataset_path};")

        df = pd.read_csv(self.training_dataset_path)
        return df.iloc[:, :-1].values, df.iloc[:, -1].values

    def load_test_data(self) -> tuple:
        if not os.path.exists(self.test_dataset_path):
            raise IOError(f"Path does not exist: {self.test_dataset_path};")

        df = pd.read_csv(self.test_dataset_path)
        return df.iloc[:, :-1].values, df.iloc[:, -1].values
