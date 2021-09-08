# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Script to create a QnA Maker knowledge base (KB) from a file
to one QnA Maker resource.

- Initial KB JSON file

This script can be run from the command line (or from inside your IDE) using:

python <path_to_this_file> --name <knowledgebase_name> --input <input_file_name>

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

    dest_client = QnaClient(
        env.qna_dest_endpoint, env.qna_dest_sub_key, env.qna_dest_kb_id
    )

    print(
        f"Destination QnA Maker - Endpoint: {env.qna_dest_endpoint} Name: {args.name}"
    )

    with open(args.input, "r", encoding="utf-8") as f:
        source_qnas = json.load(f)

    print(f"\tLoaded Source KB from file {args.input}.")

    print("\tCreate destination KB...")
    kb_id = dest_client.create_knowledgebase(args.name, source_qnas)
    print(f"\tKB with ID #{kb_id}# created.")

    print("Create completed (create-kb.py).")


def parse_arguments():
    argparse = ArgumentParser()
    argparse.add_argument(
        "-n", "--name", type=str, required=True, help="Name for the new Knowledgebase."
    )
    argparse.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input file name. File content must be JSON.",
    )
    return argparse.parse_args()


if __name__ == "__main__":
    main(parse_arguments())
