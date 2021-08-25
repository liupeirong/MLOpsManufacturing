# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from http import HTTPStatus
import json
from test_data import jsonKB, jsonKBDetails, jsonKBwOALFeedback, alMergeIntoKB, \
                      kbCreateResponse, operationStatusResponseRunning, \
                      operationStatusResponseCompleted
from unittest.mock import Mock

# record bodys captured by API POST/PUT mocks
sentBodys = []
# flag if operations is called again
operationsCalledOnce = False


def fakeQnAMakerAPI(method: str, url: str, headers, data: str = ""):
    """Faked API return data based on Method and URL
    HAPPY PATH
    """
    global operationsCalledOnce

    if method == "POST" and url == "https://localhost/dest/knowledgebases/create":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(kbCreateResponse)
        returnvalue.return_value.status_code = HTTPStatus.ACCEPTED
        # save body to variable for verification in unit test
        sentBodys.append(data)
        return returnvalue()

    if method == "GET" and url == "https://localhost/dest/operations/1":
        returnvalue = Mock()
        if operationsCalledOnce:
            returnvalue.return_value.text = json.dumps(operationStatusResponseCompleted)
        else:
            returnvalue.return_value.text = json.dumps(operationStatusResponseRunning)
            operationsCalledOnce = True
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url == "https://localhost/source/knowledgebases/123":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if (
        method == "GET"
        and url == "https://localhost/source/knowledgebases/123/Test/qna"
    ):
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKB)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url.__contains__(
        "https://localhost/dest/knowledgebases/456/Test/qna"
    ):
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKB)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "PUT" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = ""
        returnvalue.return_value.status_code = HTTPStatus.NO_CONTENT
        # save body to variable for verification in unit test
        sentBodys.append(data)
        return returnvalue()

    if method == "POST" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = ""
        returnvalue.return_value.status_code = HTTPStatus.NO_CONTENT
        sentBodys.append(data)
        return returnvalue()


def fakeQnAMakerAPIgetDetailsBroken(method, url, headers):
    """Faked API return data based on Method and URL
    getDetails Broken
    """

    if method == "GET" and url == "https://localhost/source/knowledgebases/123":
        returnvalue = Mock()
        returnvalue.return_value.text = "nonono"
        returnvalue.return_value.status_code = HTTPStatus.FORBIDDEN
        return returnvalue()


def fakeQnAMakerAPIsecondCallBroken(method, url, headers):
    """Faked API return data based on Method and URL
    second call breaks
    """

    if method == "GET" and url == "https://localhost/source/knowledgebases/123":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if (
        method == "GET"
        and url == "https://localhost/source/knowledgebases/123/Test/qna"
    ):
        returnvalue = Mock()
        returnvalue.return_value.text = "badrequest"
        returnvalue.return_value.status_code = HTTPStatus.BAD_REQUEST
        return returnvalue()


def fakeQnAMakerAPIreplaceCallBroken(method, url, headers, data: str = ""):
    """Faked API return data based on Method and URL
    second call breaks
    """

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "PUT" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = "badrequest"
        returnvalue.return_value.status_code = HTTPStatus.BAD_REQUEST
        return returnvalue()


def fakeQnAMakerAPIpublishCallBroken(method, url, headers, data: str = ""):
    """Faked API return data based on Method and URL
    second call breaks
    """

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "POST" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = "badrequest"
        returnvalue.return_value.status_code = HTTPStatus.BAD_REQUEST
        return returnvalue()


def fakeQnAMakerAPIsyncCallBroken(method, url, headers, data: str = ""):
    """Faked API return data based on Method and URL
    second call breaks
    """

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url.__contains__(
        "https://localhost/dest/knowledgebases/456/Test/qna"
    ):
        returnvalue = Mock()
        returnvalue.return_value.text = "badrequest"
        returnvalue.return_value.status_code = HTTPStatus.BAD_REQUEST
        return returnvalue()


def fakeQnAMakerAPImerge(method: str, url: str, headers, data: str = ""):
    """Faked API return data based on Method and URL
    HAPPY PATH
    """

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456/Test/qna":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBwOALFeedback)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "PUT" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = ""
        returnvalue.return_value.status_code = HTTPStatus.NO_CONTENT
        # save body to variable for verification in unit test
        sentBodys.append(data)
        return returnvalue()


def fakeQnAMakerAPImergeCallBroken(method: str, url: str, headers, data: str = ""):
    """Faked API return data based on Method and URL
    Error PATH
    """

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456/Test/qna":
        returnvalue = Mock()
        returnvalue.return_value.text = "badrequest"
        returnvalue.return_value.status_code = HTTPStatus.BAD_REQUEST
        return returnvalue()


def fakeQnAMakerAPIcomplexMerge(method: str, url: str, headers, data: str = ""):
    """Faked API return data based on Method and URL
    HAPPY PATH
    """

    if method == "GET" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(jsonKBDetails)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "GET" and url.__contains__(
        "https://localhost/dest/knowledgebases/456/Test/qna"
    ):
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(alMergeIntoKB)
        returnvalue.return_value.status_code = HTTPStatus.OK
        return returnvalue()

    if method == "PUT" and url == "https://localhost/dest/knowledgebases/456":
        returnvalue = Mock()
        returnvalue.return_value.text = ""
        returnvalue.return_value.status_code = HTTPStatus.NO_CONTENT
        # save body to variable for verification in unit test
        sentBodys.append(data)
        return returnvalue()


def fakeQnAMakerAPIcreateBroken(method: str, url: str, headers, data: str = ""):
    """Faked API return data based on Method and URL
    ERROR PATH
    """

    if method == "POST" and url == "https://localhost/dest/knowledgebases/create":
        returnvalue = Mock()
        returnvalue.return_value.status_code = HTTPStatus.BAD_REQUEST
        return returnvalue()


def fakeQnAMakerAPIoperationBroken(method: str, url: str, headers, data: str = ""):
    """Faked API return data based on Method and URL
    ERROR PATH
    """

    if method == "POST" and url == "https://localhost/dest/knowledgebases/create":
        returnvalue = Mock()
        returnvalue.return_value.text = json.dumps(kbCreateResponse)
        returnvalue.return_value.status_code = HTTPStatus.ACCEPTED
        # save body to variable for verification in unit test
        sentBodys.append(data)
        return returnvalue()

    if method == "GET" and url == "https://localhost/dest/operations/1":
        returnvalue = Mock()
        returnvalue.return_value.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return returnvalue()


def returnSentBody(index: int):
    return sentBodys[index]


def resetSentBody():
    # Reseting state for Fake API
    global sentBodys
    global operationsCalledOnce
    sentBodys = []
    operationsCalledOnce = False
