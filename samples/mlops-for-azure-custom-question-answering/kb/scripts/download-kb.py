# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Script to download a QnA Maker knowledge base (KB) from one
QnA Maker resource to a json file.

This script can be run from the command line (or from inside your IDE) using:

python <path_to_this_file> --output <output_file_name> --slot <test/prod>

Troubleshooting:

- ModuleNotFoundError: No module named 'kb'
  -> Fix: set environment variable PYTHONPATH to repo root
     e.g.: export PYTHONPATH=/workspaces/MLOpsManufacturing/samples/mlops-for-azure-custom-question-answering

"""

from kb.util.env import Env
from kb.util.qnaClient import QnaClient
from argparse import ArgumentParser, Namespace
import json


def main(args: Namespace):
    env = Env()
    # Get the details of the KBs so they can be used in output/storage
    #   folder names.
    source_client = QnaClient(
        env.qna_source_endpoint,
        env.qna_source_sub_key,
        env.qna_source_kb_id
    )

    source_kb_details = source_client.get_kb_details()

    print(
        f"Source KB - Name: {source_kb_details['name']}, "
        "ID: {env.qna_source_kb_id}, Endpoint: {env.qna_source_endpoint}"
    )

    # Download the source (where you are promoting from) KB question and
    #   answers.
    print(f"\tDownloading source KB from {args.slot}...")
    source_qnas = source_client.download(args.slot)
    print("\t\tDownloaded.")

    with open(args.output, "w", encoding='utf-8') as f:
        f.write(json.dumps(source_qnas, sort_keys=True, indent=4))

    print(f"\t\tSaved to file {args.output}.")

    print("Download completed (download-kb.py).")


def parse_arguments():
    argparse = ArgumentParser()
    argparse.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output file name. File content will be JSON.")
    argparse.add_argument(
        "-s",
        "--slot",
        choices=['Test', 'Prod'],
        required=True,
        help="Flag to determine from which slot the KB should be downloaded."
    )
    return argparse.parse_args()


if __name__ == "__main__":
    main(parse_arguments())
