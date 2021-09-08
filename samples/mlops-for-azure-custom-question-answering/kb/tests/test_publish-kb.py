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
    fakeQnAMakerAPI,
    fakeQnAMakerAPIreplaceCallBroken,
    fakeQnAMakerAPIsyncCallBroken,
    fakeQnAMakerAPIpublishCallBroken,
    returnSentBody,
    resetSentBody,
)
import json
from kb.tests.test_data import jsonKB, jsonKBwOALFeedback


def test_for_branch_completeness(mocker: MockFixture):
    """Test else Path"""
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.publish-kb", run_name="__something__")


def test_publish_sync(mocker: MockFixture):
    """Test happy Path"""
    resetSentBody()
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="y", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPI)

    fileIn = mock_open(read_data=json.dumps(jsonKBwOALFeedback["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.publish-kb", run_name="__main__")

    assert returnSentBody(0) == json.dumps({"qnAList": jsonKB["qnaDocuments"]})


def test_publish_wo_sync(mocker: MockFixture):
    """Test happy Path without sync"""
    resetSentBody()
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="n", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPI)

    fileIn = mock_open(read_data=json.dumps(jsonKBwOALFeedback["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.publish-kb", run_name="__main__")

    assert returnSentBody(0) == json.dumps(
        {"qnAList": jsonKBwOALFeedback["qnaDocuments"]}
    )


def test_publish_error_on_replace(mocker: MockFixture):
    """Test API error on replace"""
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="n", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPIreplaceCallBroken)

    fileIn = mock_open(read_data=json.dumps(jsonKBwOALFeedback["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module("kb.scripts.publish-kb", run_name="__main__")


def test_publish_error_on_publish(mocker: MockFixture):
    """Test API error on publish"""
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="n", sync_timespan="5d", publish_only=True
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPIpublishCallBroken)

    fileIn = mock_open(read_data=json.dumps(jsonKBwOALFeedback["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module("kb.scripts.publish-kb", run_name="__main__")


def test_publish_error_on_sync(mocker: MockFixture):
    """Test API error on SYNC"""
    # Mocking cmd line arguments
    testArgs = Namespace(
        input="file.in", sync_feedback="y", sync_timespan="5d", publish_only=False
    )

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPIsyncCallBroken)

    fileIn = mock_open(read_data=json.dumps(jsonKBwOALFeedback["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module("kb.scripts.publish-kb", run_name="__main__")
