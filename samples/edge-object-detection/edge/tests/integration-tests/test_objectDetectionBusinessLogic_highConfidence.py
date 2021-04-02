import asyncio
import json
import os
import sys

# Import modules from tests/
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from iotHubMessageHelper import GenerateHighConfidenceMessage
from edgeModuleTestHandler import TestHandler

test_passed = False

# This function is where we will parse back the message we expect to get
# If it is what we expect, set test_passed to True
def on_event_hub_message_received(event):
    system_properties = event.system_properties
    event_body = json.loads(event.body_as_str())
    print("Telemetry received: ", event_body)
    print("System properties (set by IoT Hub): ", system_properties)
    if system_properties[b'iothub-connection-module-id'] == b'objectDetectionBusinessLogic' and len(event_body["inferences"]) > 0:
        global test_passed
        test_passed = True

async def main(iot_hub_conn_str, event_hub_conn_str, device_id):
    test_handler = TestHandler(event_hub_conn_str, iot_hub_conn_str)
    await test_handler.runTest(on_event_hub_message_received, GenerateHighConfidenceMessage(), device_id)

if __name__ == "__main__":
    # Get connection string inputs
    iot_hub_conn_str = sys.argv[1]
    event_hub_conn_str = sys.argv[2]
    device_id = sys.argv[3]

    # Run main until test is over
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(iot_hub_conn_str, event_hub_conn_str, device_id))
    if not test_passed:
        print("Test failed")
        exit(1)
