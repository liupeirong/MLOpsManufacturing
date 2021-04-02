import os
import sys
import time
import json
import asyncio
import logging
import re

from opencensus.ext.azure.log_exporter import AzureLogHandler
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubModuleClient
from datetime import datetime, timedelta

TWIN_CALLBACKS = 0
OBJECT_TAGS = ['truck']
OBJECT_CONFIDENCE = 0.5
NOTIFICATION_TIMEOUT = '5m'
EVENT_TIMEOUT_DICT = {}
DATETIME_STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
LOG_LEVEL = 'INFO'

module_client = None
logger = logging.getLogger(__name__)

# Define behavior to keep the application running
async def continuous_loop():
    while True:
        time.sleep(100)

# twin_patch_handler is invoked when the module twin's desired properties are updated
def twin_patch_handler(patch):
    global TWIN_CALLBACKS
    global OBJECT_TAGS
    global OBJECT_CONFIDENCE
    global NOTIFICATION_TIMEOUT
    global LOG_LEVEL

    logger.debug('The data in the desired properties patch was: %s' % patch)

    if 'objectTags' in patch:
        OBJECT_TAGS = patch['objectTags']
    if 'objectConfidence' in patch:
        OBJECT_CONFIDENCE = patch['objectConfidence']
    if 'notificationTimeout' in patch:
        NOTIFICATION_TIMEOUT = patch['notificationTimeout']
    if 'logLevel' in patch:
        LOG_LEVEL = patch['logLevel']
        logger.setLevel(LOG_LEVEL)

    TWIN_CALLBACKS += 1
    logger.debug('Total calls confirmed: %d\n' % TWIN_CALLBACKS)

# Define behavior for receiving an input message on the 'detectedObjects' route
async def message_handler(message):
    if message.input_name == 'detectedObjects':
        logger.debug('Message received on detectedObjects route')
        await object_detected_handler(message)
    else:
        logger.warning('Message received on unknown input route')

# object_detected_handler checks the AI inferrencing result and sends a message to the
# 'eventAlertTrigger` output message route when all conditions are met
async def object_detected_handler(input_message):
    try:
        if input_message is None:
            logger.warning('input_message is None')
            return

        # List to hold inferences with desired tag and confidence level
        inferences = []

        message = input_message.data.decode('utf-8')
        data = json.loads(message)

        detected_objects = data['inferences']
        graph_instance = extract_graph_instance_from_subject(input_message.custom_properties['subject'])

        logger.info(f'{graph_instance}: Detected {len(detected_objects)} object(s)')

        for inference in detected_objects:
            entity = inference['entity']
            tag = entity['tag']
            confidence = tag['confidence']
            detected_object = tag['value']

            event_data = {
                'detected_object': detected_object,
                'confidence': confidence,
                'graph_instance': graph_instance
            }

            logger.info(f'{graph_instance}: {detected_object} detected. Confidence: {confidence}', extra={'custom_dimensions': event_data})

            if (detected_object.lower() in OBJECT_TAGS) and (confidence > OBJECT_CONFIDENCE):
                logger.info(f'>>>>> Match found: {tag} <<<<<')
                inferences.append(inference)

        if len(inferences) > 0:
            event_time = input_message.custom_properties['eventTime']
            should_send_message = check_event_timeout(event_time, input_message.custom_properties['subject'])

            logger.debug(f'Send message: {should_send_message}')

            if should_send_message:
                output_message = construct_output_message(
                    graph_instance,
                    input_message.custom_properties['$.cdid'],
                    inferences,
                    event_time)
                output_message_route = 'Event-' + graph_instance
                await module_client.send_message_to_output(output_message, output_message_route)

    except Exception as ex:
        logger.exception('Unexpected error: %s' % ex)

# extract_graph_instance_from_subject extracts the graph instance name from the subject
# e.g. given "/graphInstances/Truck/processors/inferenceClient" the output will be "Truck"
def extract_graph_instance_from_subject(subject):
    if subject is None:
        raise Exception('subject is None')

    graph_instance_signature = '/graphInstances/'

    if graph_instance_signature not in subject:
        raise Exception('Graph instance signature is not present in subject')

    words = subject.split('/')
    return words[2]

# check_event_timeout determines if we should send a message for a given graph instance based on the
# notification time out value. For example, we may only want to send a message for the same graph instance
# every 5 minutes to avoid spam messages.
def check_event_timeout(event_time, subject):
    graph_instance = extract_graph_instance_from_subject(subject)
    input_msg_event_time_object = datetime.strptime((event_time), DATETIME_STRING_FORMAT)

    if NOTIFICATION_TIMEOUT == '0' or NOTIFICATION_TIMEOUT == '0s':
        EVENT_TIMEOUT_DICT[graph_instance] = 0
        return True

    logger.debug(f'Current input time: {input_msg_event_time_object}')

    if graph_instance in EVENT_TIMEOUT_DICT and input_msg_event_time_object <= EVENT_TIMEOUT_DICT[graph_instance]:
        logger.debug(f'This message already exists, but it\'s timeout of {NOTIFICATION_TIMEOUT} is still active')
        return False
    else:
        timeout_seconds = time_to_seconds(NOTIFICATION_TIMEOUT)

        if timeout_seconds == -1:
            timeout_seconds = 900
            logger.warning('NOTIFICATION_TIMEOUT is not configured correctly, defaulting to 15m')

        EVENT_TIMEOUT_DICT[graph_instance] = input_msg_event_time_object + timedelta(seconds=timeout_seconds)

        logger.debug('Adding this event for the first time or updating to a new timeout')
        logger.debug(f'New input time: {EVENT_TIMEOUT_DICT[graph_instance]}')

        return True

# construct_output_message creates the output message we will send to IoT Hub
def construct_output_message(graph_instance, device_id, inferences, event_time):
    logger.debug("Constructing output message")

    output_dict = {
        'graphInstance': graph_instance,
        'deviceId': device_id,
        'inferences': inferences,
        'eventTime': event_time
    }

    output_message_string = json.dumps(output_dict)
    output_message = Message(output_message_string, content_encoding='utf-8')

    logger.debug(f'Output message: {output_message}')
    return output_message

# Function which translates time from format '(\d+)([smh]' to value in seconds.
def time_to_seconds(time_string):
    if time_string is None:
        logger.error('Input string cannot be None')
        return -1

    time_re = re.search(r'(\d+)([smh])', time_string)

    if time_re is None or len(time_re.groups()) < 2:
        logger.error('Could not parse time')
        return -1

    time_unit = time_re.groups()[1]
    time_value = int(time_re.groups()[0])

    if time_unit == 'm':
        time_value *= 60
    elif time_unit == 'h':
        time_value *= 3600
    return time_value

async def main():
    global module_client

    logger.setLevel(LOG_LEVEL)

    # ODBL: Object Detection Business Logic
    formatter = logging.Formatter('[ODBL] [%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s')

    # Add stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    appinsights_instrumentationkey = os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY', None)
    if appinsights_instrumentationkey and not appinsights_instrumentationkey.isspace():
        try:
            azure_log_handler = AzureLogHandler(instrumentation_key=appinsights_instrumentationkey)
            azure_log_handler.setFormatter(formatter)
            logger.addHandler(azure_log_handler)

            logger.info('Application Insights initialized.')
        except Exception:
            logger.exception('Application Insights failed to initialize')

    try:
        if not sys.version >= '3.6':
            raise Exception('The object detection business logic module requires python 3.6+. Current version of Python: %s' % sys.version)

        logger.info('Starting the object detection business logic module ...')

        module_client = IoTHubModuleClient.create_from_edge_environment(websockets=True)

        await module_client.connect()
        module_client.on_twin_desired_properties_patch_received = twin_patch_handler
        module_client.on_message_received = message_handler

        logger.info('The object detection business logic module is now waiting for messages.')

        await continuous_loop()
        await module_client.disconnect()
    except Exception as ex:
        logger.exception('Unexpected error: %s' % ex)
        return

if __name__ == '__main__':
    asyncio.run(main())
