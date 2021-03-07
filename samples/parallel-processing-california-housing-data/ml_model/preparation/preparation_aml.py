"""Preparation wrapper: script to be executed when running Preparation Step."""

from logging import INFO, Formatter, StreamHandler, getLogger
from pathlib import Path

import click
from azureml.core import Datastore, Run


def run(input_path: str, output_path: str, datastore_name: str):
    """Run Function.

    Args:
        input_path (str): path to raw text files in the datastore
        output_path (str): path to the output directory
        datastore_name (str): name of the datastore
    """
    logger.info("PREPARATION")
    logger.info(f"input files path: {input_path}")
    logger.info(f"output directory path: {output_path}")

    Path(output_path).mkdir(parents=True, exist_ok=True)

    # Download input datasets
    run = Run.get_context()
    workspace = run.experiment.workspace

    shared_blob_store = Datastore.get(workspace, datastore_name)
    shared_blob_store.download(target_path=output_path, prefix=input_path)


@click.command()
@click.option("--input_path", type=str, help="path to raw text files in the datastore", default="/tmp/input_path")
@click.option("--output_path", type=str, help="path to the output directory", default="/tmp/output_path")
@click.option("--datastore_name", type=str, help="name of the datastore", default="blobdatastore")
def main(input_path: str, output_path: str, datastore_name: str):
    """Execuete run function.

    Args:
        input_path (str): path to raw text files in the datastore
        output_path (str): path to the output directory
        datastore_name (str): name of the datastore
    """
    run(input_path, output_path, datastore_name)


if __name__ == "__main__":
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    logger.propagate = False
    sh = StreamHandler()
    sh.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)
    main()
