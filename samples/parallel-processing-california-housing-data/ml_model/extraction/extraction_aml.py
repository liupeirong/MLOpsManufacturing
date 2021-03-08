"""Extraction Step wrapper: script to be executed when running Extraction Step."""
import argparse
import json
from logging import INFO, Formatter, StreamHandler

from azureml_user.parallel_run import EntryScript

args = None
logger = None


def init():
    """Init function."""
    global args
    global logger

    entry_script = EntryScript()
    logger = entry_script.logger
    logger.setLevel(INFO)
    logger.propagate = False
    sh = StreamHandler()
    sh.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(sh)

    parser = argparse.ArgumentParser(description="Extraction Parallel Running")
    parser.add_argument('--output_dir', dest="output_dir", required=True, type=str, default="/tmp/extraction/output")

    args, _ = parser.parse_known_args()


def run(mini_batch):
    """Run Function.

    Args:
        mini_batch (List): file paths of the raw text files to be consumed

    Returns:
        List: result of the run
    """
    global args
    global logger

    logger.info("Extraction Step")

    result_list = []
    for raw_file in mini_batch:
        with open(raw_file) as r_file:
            data_row = {}
            for line in r_file.readlines():
                item = line.split(":")
                data_row[item[0].strip()] = item[1].strip()

            result_list.append(json.dumps(data_row))

    return result_list
