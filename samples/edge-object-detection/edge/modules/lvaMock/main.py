import asyncio
import json
import sys
import time

from azure.iot.device import Message, MethodResponse
from azure.iot.device.aio import IoTHubModuleClient

module_client = None

# Define behavior to keep the application running
async def continuous_loop():
    while True:
        time.sleep(100)

# Define behavior for receiving an input method
async def method_request_handler(method_request):
    print("Received message")
    print(method_request.payload)
    status = 400  # set return status code

    if method_request.name == 'invokeDetectedObjectsMessage':
        print("Calling function to output detectedObjects message")
        status = await send_detectedObjects_message(method_request.payload)
    else:
        print('Message received on unknown input route')

    print("Sent detectedObjects message")
    method_response = MethodResponse.create_from_method_request(method_request, status)
    await module_client.send_method_response(method_response)

async def send_detectedObjects_message(message):
    try:
        output_message = Message(json.dumps(message["body"]))
        output_message.custom_properties = message["properties"]
        print("Sending detectedObjects message")
        await module_client.send_message_to_output(output_message, "detectedObjects")
        return 200
    except Exception as ex:
        print('Unexpected error from sending message: %s' % ex)
        return 400

async def main():
    global module_client
    try:
        if not sys.version >= '3.6':
            raise Exception('The object detection business logic module requires python 3.6+. Current version of Python: %s' % sys.version)

        print("Starting lvaMock edge module")
        module_client = IoTHubModuleClient.create_from_edge_environment(websockets=True)
        await module_client.connect()
        module_client.on_method_request_received = method_request_handler

        await continuous_loop()
        await module_client.disconnect()
    except Exception as ex:
        print('Unexpected error from IoTHub: %s' % ex)
        return

if __name__ == '__main__':
    asyncio.run(main())
