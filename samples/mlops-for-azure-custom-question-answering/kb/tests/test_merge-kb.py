# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from argparse import Namespace
import builtins
import runpy
import pytest
from unittest.mock import mock_open
from pytest_mock import MockFixture
from kb.tests.test_fixtures import environment_vars  # noqa: F401
from kb.tests.fake_api import (
    fakeQnAMakerAPImerge,
    returnSentBody,
    fakeQnAMakerAPImergeCallBroken,
    resetSentBody,
    fakeQnAMakerAPIcomplexMerge,
)
import json
from kb.tests.test_data import jsonKB, alMergeExpectedResult, alMergeFromKB


def test_for_branch_completeness(mocker: MockFixture):
    """Test else Path"""
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.merge-kb", run_name="__something__")


def test_merge_single(mocker: MockFixture):
    """Test happy Path"""
    resetSentBody()
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="y", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPImerge)

    fileIn = mock_open(read_data=json.dumps(jsonKB["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.merge-kb", run_name="__main__")

    assert returnSentBody(0) == json.dumps({"qnAList": jsonKB["qnaDocuments"]})


def test_merge_failure(mocker: MockFixture):
    """Merge Failure on merge"""
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="y", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPImergeCallBroken)

    fileIn = mock_open(read_data=json.dumps(jsonKB["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module("kb.scripts.merge-kb", run_name="__main__")


def test_merge_complex(mocker: MockFixture):
    """Test happy Path with complex result"""
    resetSentBody()
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="y", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPIcomplexMerge)

    fileIn = mock_open(read_data=json.dumps(alMergeFromKB["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.merge-kb", run_name="__main__")

    assert returnSentBody(0) == json.dumps(
        {"qnAList": alMergeExpectedResult["qnaDocuments"]}
    )
