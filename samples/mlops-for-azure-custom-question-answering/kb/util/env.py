# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Env class to load and hold all environment variables.
"""
import os
from typing import Optional
from dotenv import load_dotenv


class Env:
    """Loads all environment variables into a predefined set of properties."""

    def __init__(self, path_to_env: str = None):
        # Load dev.env file into environment variables for local execution
        load_dotenv(dotenv_path=path_to_env)

        # Variables that are used by the control plane scripts but are
        # never passed on to the pipeline steps.
        self.qna_source_sub_key: Optional[str] = os.environ.get(
                "QNA_SOURCE_SUB_KEY"
            )
        self.qna_source_endpoint: Optional[str] = os.environ.get(
                "QNA_SOURCE_ENDPOINT"
            )
        self.qna_source_kb_id: Optional[str] = os.environ.get(
                "QNA_SOURCE_KB_ID"
            )

        self.qna_dest_sub_key: Optional[str] = os.environ.get(
                "QNA_DEST_SUB_KEY"
            )
        self.qna_dest_endpoint: Optional[str] = os.environ.get(
                "QNA_DEST_ENDPOINT"
            )
        self.qna_dest_kb_id: Optional[str] = os.environ.get(
                "QNA_DEST_KB_ID"
            )
