# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
from pytest_mock import MockFixture
import os


@pytest.fixture(autouse=True)
def environment_vars(mocker: MockFixture):
    """environment_vars
    Auto fixture - will be always present if imported by unit tests
    Sets basic env variables.
    """
    mocker.patch.dict(
        os.environ,
        {
            "QNA_SOURCE_SUB_KEY": "sourceKey",
            "QNA_SOURCE_ENDPOINT": "https://localhost/source/",
            "QNA_SOURCE_KB_ID": "123",
            "QNA_DEST_SUB_KEY": "destKey",
            "QNA_DEST_ENDPOINT": "https://localhost/dest",
            "QNA_DEST_KB_ID": "456",
        },
    )

    return environment_vars
