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
    fakeQnAMakerAPIgetDetailsBroken,
    fakeQnAMakerAPIsecondCallBroken,
)
import json
from kb.tests.test_data import jsonKB


def test_for_branch_completeness(mocker: MockFixture):
    """Test else Path"""
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.download-kb", run_name="__something__")


def test_download(mocker: MockFixture):
    """Test happy Path"""
    # Mocking cmd line arguments
    testArgs = Namespace(output="file.out", slot="Test")
    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPI)

    fileOut = mock_open()
    mocker.patch.object(builtins, "open", fileOut)
    # run as module (start from if __name__ == "__main__")
    runpy.run_module("kb.scripts.download-kb", run_name="__main__")

    fileOut.assert_called_once_with("file.out", "w", encoding="utf-8")

    fileOut().write.assert_called_with(
        json.dumps(jsonKB["qnaDocuments"], sort_keys=True, indent=4)
    )


def test_connection_error_on_getDetails(mocker: MockFixture):
    """Test connection error"""
    # Mocking cmd line arguments
    testArgs = Namespace(output="file.out", slot="Test")
    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPIgetDetailsBroken)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module("kb.scripts.download-kb", run_name="__main__")


def test_connection_error_on_downloadkb(mocker: MockFixture):
    """Test connection error"""
    # Mocking cmd line arguments
    testArgs = Namespace(output="file.out", slot="Test")
    mocker.patch("argparse.ArgumentParser.parse_args", return_value=testArgs)

    mocker.patch("requests.request", side_effect=fakeQnAMakerAPIsecondCallBroken)

    with pytest.raises(Exception):
        # run as module (start from if __name__ == "__main__")
        runpy.run_module("kb.scripts.download-kb", run_name="__main__")
