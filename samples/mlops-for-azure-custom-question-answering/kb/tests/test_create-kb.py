# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from argparse import Namespace
import builtins
import runpy
import pytest
from unittest.mock import mock_open
from pytest_mock import MockFixture
from kb.tests.test_fixtures import environment_vars  # noqa: F401
from kb.tests.fake_api import fakeQnAMakerAPI, returnSentBody, resetSentBody, \
                              fakeQnAMakerAPIcreateBroken, fakeQnAMakerAPIoperationBroken
import json
from kb.tests.test_data import jsonKB


def test_for_branch_completeness(mocker: MockFixture):
    """Test else Path"""
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.create-kb", run_name="__something__")


def test_create_sync(mocker: MockFixture):
    """Test happy Path"""
    resetSentBody()
    # Mocking cmd line arguments
    kbName = "QnA Maker Test"
    testArgs = Namespace(input="file.in", name=kbName)

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPI)

    fileIn = mock_open(read_data=json.dumps(jsonKB["qnaDocuments"]))
    mocker.patch.object(builtins, "open", fileIn)
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.create-kb", run_name="__main__")

    assert returnSentBody(0) == json.dumps(
        {"name": kbName, "qnaList": jsonKB["qnaDocuments"]}
    )


def test_create_error_on_create(mocker: MockFixture):
    """ Test API error on create
    """
    # Mocking cmd line arguments
    kbName = "QnA Maker Test"
    testArgs = Namespace(input="file.in", name=kbName)

    mocker.patch('argparse.ArgumentParser.parse_args',
                 return_value=testArgs)

    mocker.patch('requests.request', side_effect=fakeQnAMakerAPIcreateBroken)

    fileIn = mock_open(read_data=json.dumps(jsonKB['qnaDocuments']))
    mocker.patch.object(builtins, 'open', fileIn)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module('kb.scripts.create-kb',
                         run_name='__main__')


def test_publish_error_on_operation(mocker: MockFixture):
    """ Test API error on operation status check
    """
    # Mocking cmd line arguments
    kbName = "QnA Maker Test"
    testArgs = Namespace(input="file.in", name=kbName)

    mocker.patch('argparse.ArgumentParser.parse_args',
                 return_value=testArgs)

    mocker.patch('requests.request', side_effect=fakeQnAMakerAPIoperationBroken)

    fileIn = mock_open(read_data=json.dumps(jsonKB['qnaDocuments']))
    mocker.patch.object(builtins, 'open', fileIn)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module('kb.scripts.create-kb',
                         run_name='__main__')
