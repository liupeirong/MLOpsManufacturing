import os
import sys

import json
import pytest
import asyncio
import logging

from testfixtures import LogCapture
from unittest import TestCase
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

# Import main.py from objectDetectionBusinessLogic edge module
sys.path.append(os.path.join(os.path.dirname(__file__), '../../modules/objectDetectionBusinessLogic'))
import main

# Import message helper from tests/
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from iotHubMessageHelper import GenerateDetectedObjectsMessage

logger = logging.getLogger('')

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs"""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

class TestTwinPatchHandlerFunction(TestCase):
    """Unit tests for twin_patch_handler function"""

    def setUp(self):
        super(TestTwinPatchHandlerFunction, self).setUp()
        main.TWIN_CALLBACKS = 0
        main.OBJECT_TAGS = []
        main.OBJECT_CONFIDENCE = 0
        main.NOTIFICATION_TIMEOUT = ''

    def tearDown(self):
        super(TestTwinPatchHandlerFunction, self).tearDown()
        main.TWIN_CALLBACKS = 0
        main.OBJECT_TAGS = ['truck']
        main.OBJECT_CONFIDENCE = 0.5
        main.NOTIFICATION_TIMEOUT = '2m'

    def test_message_handler_twin_patch_handler_objectTags(self):
        main.twin_patch_handler({"objectTags": ["apple"]})

        assert main.OBJECT_TAGS == ['apple']
        assert main.TWIN_CALLBACKS == 1

    def test_message_handler_twin_patch_handler_objectConfidence(self):
        main.twin_patch_handler({"objectConfidence": 0.3})

        assert main.OBJECT_CONFIDENCE == 0.3
        assert main.TWIN_CALLBACKS == 1

    def test_message_handler_twin_patch_handler_notificationTimeout(self):
        main.twin_patch_handler({"notificationTimeout": "23s"})

        assert main.NOTIFICATION_TIMEOUT == "23s"
        assert main.TWIN_CALLBACKS == 1

class TestMessageHandlerFunction():
    """Unit tests for message_handler function"""

    @pytest.mark.parametrize('test_input,expected', [
        ('detectedObjects', 'Message received on detectedObjects route'),
        ('anything', 'Message received on unknown input route'),
        (' ', 'Message received on unknown input route')
    ])
    def test_message_handler_detectedObjects_route(self, test_input, expected):
        with LogCapture() as logs:
            source = GenerateDetectedObjectsMessage(test_input, 'car', 0.7)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main.message_handler(source))
        assert expected in str(logs)

    def test_message_handler_empty_route(self):
        with LogCapture() as logs:
            source = GenerateDetectedObjectsMessage(None, 'car', 0.7)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main.message_handler(source))
        assert 'Message received on unknown input route' in str(logs)

class TestObjectDetectedHandlerFunction():
    """Unit tests for check_event_timeout function"""

    @pytest.mark.parametrize('input_message,event_dict,timeout', [
        ('None', {}, None),
        ('', {}, 1)
    ])
    def test_object_detected_handler_invalid_values_throws_exception(self, input_message, event_dict, timeout):
        with(patch('main.NOTIFICATION_TIMEOUT', timeout)):
            with(patch('main.EVENT_TIMEOUT_DICT', event_dict)):
                with pytest.raises(Exception):
                    loop = asyncio.run()
                    loop.run_until_complete(main.object_detected_handler(input_message))

    @pytest.mark.parametrize('event_dict,timeout,expected_call_count,expected_time,confidence,tag', [
        ({}, '1s', 1, '2020-11-24T19:22:06.912000Z', 0.7, 'truck'),
        ({'Truck': datetime.strptime(('2020-11-24T19:22:05.912Z'), '%Y-%m-%dT%H:%M:%S.%fZ')}, '1s', 0, '2020-11-24T19:22:05.912000Z', 0.8, 'truck'),
        ({}, '1s', 0, '2020-11-24T19:22:05.912000Z', 0.1, 'truck'),
        ({}, '1s', 0, '2020-11-24T19:22:06.912000Z', 0.9, 'apple')
    ])
    def test_object_detected_handler(self, event_dict, timeout, expected_call_count, expected_time, confidence, tag):
        mock = Mock()
        mock.send_message_to_output.return_value = True

        with LogCapture() as logs:
            with(patch('main.NOTIFICATION_TIMEOUT', timeout)):
                with(patch('main.EVENT_TIMEOUT_DICT', event_dict)):
                    with (patch('main.module_client', mock)):
                        sample_message = GenerateDetectedObjectsMessage('detectedObjects', tag, confidence)
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(main.object_detected_handler(sample_message))

                        assert mock.send_message_to_output.call_count == expected_call_count

                        if 'Truck' in main.EVENT_TIMEOUT_DICT:
                            assert main.EVENT_TIMEOUT_DICT['Truck'].strftime('%Y-%m-%dT%H:%M:%S.%fZ') == expected_time

        events = [r.custom_dimensions for r in logs.records if 'detected' in r.msg]
        assert len(events) == 1
        assert events[0]['detected_object'] == tag
        assert events[0]['confidence'] == confidence
        assert events[0]['graph_instance'] == 'Truck'

class TestTimeToSecondsFunction():
    """Unit tests for time_to_seconds function"""

    @pytest.mark.parametrize('test_input,expected', [
        ('10s', 10),
        ('10m', 600),
        ('10h', 36000)
    ])
    def test_time_to_seconds_input_is_correct(self, test_input, expected):
        result = main.time_to_seconds(test_input)
        assert result == expected

    @pytest.mark.parametrize('test_input', [
        'm5',
        'words',
        '5',
        ' '
    ])
    def test_time_to_seconds_input_is_incorrect(self, test_input):
        result = main.time_to_seconds(test_input)
        assert result == -1

    def test_time_to_seconds_input_is_none(self):
        result = main.time_to_seconds(None)
        assert result == -1

class TestCheckEventTimeoutFunction():
    """Unit tests for check_event_timeout function"""

    @pytest.mark.parametrize('event_time,subject,event_dict,timeout', [
        ('2020-11-24', '/graphInstances/Truck', {}, None),
        ('2020-11-24T10:00:00.00Z', '', {}, None),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, 1)
    ])
    def test_check_event_timeout_invalid_values_throws_exception(self, event_time, subject, event_dict, timeout):
        with(patch('main.NOTIFICATION_TIMEOUT', timeout)):
            with(patch('main.EVENT_TIMEOUT_DICT', event_dict)):
                with pytest.raises(Exception):
                    main.check_event_timeout(event_time, subject)

    @pytest.mark.parametrize('event_time,subject,event_dict,timeout,expected', [
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, '1s', True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, '1m', True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, '1h', True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {'Truck': datetime(2020, 11, 23, 10)}, '1m', True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {'Truck': datetime(2020, 11, 25, 10)}, '1m', False)
    ])
    def test_check_event_timeout(self, event_time, subject, event_dict, timeout, expected):
        with(patch('main.NOTIFICATION_TIMEOUT', timeout)):
            with(patch('main.EVENT_TIMEOUT_DICT', event_dict)):
                result = main.check_event_timeout(event_time, subject)

                # if True, then we are expecting a change to EVENT_TIMEOUT_DICT
                if expected:
                    event_time_obj = datetime.strptime((event_time), "%Y-%m-%dT%H:%M:%S.%fZ")
                    expected_time = event_time_obj + timedelta(seconds=main.time_to_seconds(timeout))
                    assert main.EVENT_TIMEOUT_DICT['Truck'] == expected_time

        assert result == expected

    @pytest.mark.parametrize('event_time,subject,event_dict,timeout,expected', [
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, None, True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, '1l', True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, 'words', True)
    ])
    def test_check_event_timeout_default_timeout(self, event_time, subject, event_dict, timeout, expected):
        with(patch('main.NOTIFICATION_TIMEOUT', timeout)):
            with(patch('main.EVENT_TIMEOUT_DICT', event_dict)):
                result = main.check_event_timeout(event_time, subject)

                # if True, then we are expecting a change to EVENT_TIMEOUT_DICT
                if expected:
                    timeout = '15m'  # our default timout is 15 minutes

                    event_time_obj = datetime.strptime((event_time), "%Y-%m-%dT%H:%M:%S.%fZ")
                    expected_time = event_time_obj + timedelta(seconds=main.time_to_seconds(timeout))
                    assert main.EVENT_TIMEOUT_DICT['Truck'] == expected_time

        assert result == expected

    @pytest.mark.parametrize('event_time,subject,event_dict,timeout,expected', [
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, '0', True),
        ('2020-11-24T10:00:00.00Z', '/graphInstances/Truck', {}, '0s', True),
    ])
    def test_check_event_timeout_disable_feature(self, event_time, subject, event_dict, timeout, expected):
        with(patch('main.NOTIFICATION_TIMEOUT', timeout)):
            with(patch('main.EVENT_TIMEOUT_DICT', event_dict)):
                result = main.check_event_timeout(event_time, subject)
                assert main.EVENT_TIMEOUT_DICT['Truck'] == 0
        assert result == expected

class TestExtractInstanceFromSubjectFunction():
    """Unit tests for extract_graph_instance_from_subject function"""

    @pytest.mark.parametrize('test_input,expected', [
        ('/graphInstances/Truck/processors/inferenceClient', 'Truck'),
        ('/graphInstances/Truck/', 'Truck')
    ])
    def test_extract_graph_instance_from_subject_input_is_correct(self, test_input, expected):
        result = main.extract_graph_instance_from_subject(test_input)
        assert result == expected

    @pytest.mark.parametrize('test_input', [
        'helloworld',
        'helloworld/',
        ' ',
        None
    ])
    def test_extract_graph_instance_from_subject_input_is_incorrect(self, test_input):
        with pytest.raises(Exception):
            main.extract_graph_instance_from_subject(test_input)

    @pytest.mark.parametrize('test_input', [
        '/Truck/processors/inferenceClient',
        '/placeholder/Truck/processors/inferenceClient',
        ' ',
        None
    ])
    def test_extract_graph_instance_from_subject_signature_is_missing(self, test_input):
        with pytest.raises(Exception):
            main.extract_graph_instance_from_subject(test_input)

class TestConstructOutputMessage():
    """Unit tests for construct_output_message function"""

    @pytest.mark.parametrize('graph_instance,device_id,inferences,event_time,expected_confidence ', [
        (
            'Truck',
            'lva-sample-device',
            [{
                "type": "entity",
                "subtype": "",
                "inferenceId": "",
                "relatedInferences": [],
                "entity": {
                    "tag": {
                        "value": "truck",
                        "confidence": 0.67118937
                    },
                    "box": {
                        "l": 0.58121043,
                        "t": 0.55947006,
                        "w": 0.0814074,
                        "h": 0.06241543
                    }
                },
                "extensions": {},
                "valueCase": "entity"
            }],
            '2020-12-01T19:45:50.821Z',
            0.67118937)
    ])
    def test_construct_output_message_default_msg(
        self,
        graph_instance,
        device_id,
        inferences,
        event_time,
        expected_confidence
    ):
        result = main.construct_output_message(graph_instance, device_id, inferences, event_time)

        message = result.data
        data = json.loads(message)

        assert data['graphInstance'] == graph_instance
        assert data['deviceId'] == device_id
        assert data['inferences'][0]['entity']['tag']['confidence'] == expected_confidence
