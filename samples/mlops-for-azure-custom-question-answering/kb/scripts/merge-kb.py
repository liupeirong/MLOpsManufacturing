# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Script to merge Active Learning Feedback from
a QnA Maker knowledge base (KB) from a file
to one QnA Maker resource.

- Load Incoming Active Learning feedback KB JSON file
- Merge Active Learning Feedback into KB from target QnA Maker Test slot
- Replace KB in target QnA Maker

This script can be run from the command line (or from inside your IDE) using:

python <path_to_this_file> --input <input_file_name>

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
        env.qna_dest_endpoint,
        env.qna_dest_sub_key,
        env.qna_dest_kb_id
    )

    dest_kb_details = dest_client.get_kb_details()

    print(
        f"Destination KB - Name: {dest_kb_details['name']}, ID: {env.qna_dest_kb_id}, Endpoint: {env.qna_dest_endpoint}"
    )

    with open(args.input, "r", encoding='utf-8') as f:
        incoming_qnas = json.load(f)

    print(f"\tLoaded Incoming Active Learning Feedback KB from file {args.input}.")

    print("\tMerging Feedback from Incoming KB to Destination KB...")
    destination_qnas = dest_client.merge_feedback(
            incoming_qnas
        )
    print("\t\tSynced.")

    print("\tReplace destination KB...")
    dest_client.replace_knowledgebase(destination_qnas)
    print("\t\tReplaced.")

    print("Merge completed (merge-kb.py).")


def parse_arguments():
    argparse = ArgumentParser()
    argparse.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input file name. File content must be JSON.")
    return argparse.parse_args()


if __name__ == "__main__":
    main(parse_arguments())
