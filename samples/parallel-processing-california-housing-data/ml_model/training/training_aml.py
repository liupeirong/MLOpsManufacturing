"""Training wrapper: script to be executed when running Utterance Step."""

import json
from logging import INFO, Formatter, StreamHandler, getLogger
from pathlib import Path, PurePath

import click
import joblib
import pandas as pd
from azureml.core import Run
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def run(input_dir: str, output_dir: str):
    """Run Function.

    Args:
        input_dir (str): [description]
        output_dir (str): [description]
    """
    logger.info("TRAINING")
    logger.info(f"input dir path: {input_dir}")
    logger.info(f"output dir path: {output_dir}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    data = []
    input_file = str(PurePath(input_dir, "extraction_output.txt"))
    with open(input_file) as i_file:
        for line in i_file.readlines():
            data.append(json.loads(line))
    df = pd.DataFrame.from_records(data)

    logger.info(df.describe())

    X = df.drop('price', axis=1)
    y = df['price']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    lin_reg_model = LinearRegression()
    lin_reg_model.fit(X_train, y_train)

    predict = lin_reg_model.predict(X_test)
    logger.info(f'Predicted Value :{predict[0]}')
    logger.info(f'Actual Value :{y_test.values[0]}')

    model_path = str(PurePath(output_dir, "LinRegModel"))
    joblib.dump(value=lin_reg_model, filename=model_path)

    run = Run.get_context()
    run.upload_file("models", model_path)
    run.register_model(model_name="California_Housing_Price_Prediction_Model", model_path="models", description='Generated model in Azure ML')


@click.command()
@click.option("--input_dir", type=str, help="File path of the input", default="/tmp/training_input")
@click.option("--output_dir", type=str, help="File path of the output", default="/tmp/training_output")
def main(input_dir: str, output_dir: str):
    """Execuete run function.

    Args:
        input_dir (str): File path of the input
        output_dir (str):File path of the output
    """
    run(input_dir, output_dir)


if __name__ == "__main__":
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    logger.propagate = False
    sh = StreamHandler()
    sh.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)
    main()
