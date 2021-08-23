# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Script to publish a QnA Maker knowledge base (KB) from a file
to one QnA Maker resource. Merges Active Learning Feedback from
the destination KB before publishing.

- Load KB JSON file
- Merge Active Learning Feedback from Test slot
- Replace KB in target QnA Maker
- Publish KB in target QnA Maker

This script can be run from the command line (or from inside your IDE) using:

python <path_to_this_file> --publish_only --input <input_file_name>
    --sync_feedback <y/n> --sync_timespan <timespan e.g. 5d>

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

    if(not args.publish_only):
        with open(args.input, "r", encoding='utf-8') as f:
            source_qnas = json.load(f)

        print(f"\tLoaded Source KB from file {args.input}.")

        if(args.sync_feedback == "y"):
            print("\tSyncing Feedback from Destination KB to Source KB...")
            source_qnas = dest_client.sync_feedback(
                    source_qnas,
                    args.sync_timespan
                )
            print("\t\tSynced.")

        print("\tReplace destination KB...")
        dest_client.replace_knowledgebase(source_qnas)
        print("\t\tReplaced.")

    print("\tPublish destination KB...")
    dest_client.publish_knowledgebase()
    print("\t\tPublished.")

    print("Publish completed (publish-kb.py).")


def parse_arguments():
    argparse = ArgumentParser()
    argparse.add_argument(
        "-i",
        "--input",
        type=str,
        help="Input file name. File content must be JSON.")
    argparse.add_argument(
        "-p",
        "--publish_only",
        action='store_true',
        help="Publish only without replacing. Default: False")
    argparse.add_argument(
        "-sf",
        "--sync_feedback",
        choices=['y', 'n'],
        help="Flag to Sync missing Active Learning Feedback in Destination to Source KB"
    )
    argparse.add_argument(
        "-st",
        "--sync_timespan",
        type=str,
        help="The amount of time to retroactively sync Active Feedback. E.g. '5d' for 5 days in the past."
    )
    return argparse.parse_args()


if __name__ == "__main__":
    main(parse_arguments())
