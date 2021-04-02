import asyncio
import json
from azure.eventhub.aio import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

class EventHubListener:
    def __init__(self, connection_string):
        # Set up event hub receiver
        self.event_hub_client = EventHubConsumerClient.from_connection_string(
            conn_str=connection_string,
            consumer_group="$default",
        )

    async def start_listening(self, receive_event_handler, max_wait_time=10):
        print("Starting listening")
        self.receive_event_handler = receive_event_handler
        self.recv_task = asyncio.ensure_future(self.event_hub_client.receive(on_event=self.receive_event, max_wait_time=max_wait_time))

        # Sleep so event hub receiver is up and running
        await asyncio.sleep(4)

    async def stop_listening(self):
        print("Stopping listening")
        self.recv_task.cancel()
        await self.event_hub_client.close()

    async def receive_event(self, partition_context, event):
        self.receive_event_handler(event)
        await partition_context.update_checkpoint(event)

class IoTHubHandler:
    def __init__(self, iot_hub_connection_string):
        self.registry_manager = IoTHubRegistryManager(iot_hub_connection_string)

    async def send_message(self, message, device_id, module_id, method_name):
        payload = {"body": json.loads(message.data), "properties": message.custom_properties}
        module_method = CloudToDeviceMethod(
            method_name=method_name,
            payload=payload,
            response_timeout_in_seconds=30)

        print("Invoking message called")
        resp = self.registry_manager.invoke_device_module_method(device_id, module_id, module_method)
        if resp.payload is not None:
            print(json.dumps(resp.payload))

class TestHandler:
    def __init__(self, event_hub_connection_string, iot_hub_connection_String):
        self.event_hub_connection_string = event_hub_connection_string
        self.iot_hub_connection_String = iot_hub_connection_String
        self.test_over = False

    async def runTest(self, on_message_received, message_to_send, device_id, module_id="lvaEdge", method_name="invokeDetectedObjectsMessage"):
        # Set up event hub receiver
        event_hub_listener = EventHubListener(self.event_hub_connection_string)
        await event_hub_listener.start_listening(self.eventReceived)
        self.receive_event_handler = on_message_received

        # Set up iot hub handler
        iot_hub_handler = IoTHubHandler(self.iot_hub_connection_String)
        await iot_hub_handler.send_message(message_to_send, device_id, module_id, method_name)

        # Loop until test is complete
        while(True):
            await asyncio.sleep(1)
            if(self.test_over):
                await event_hub_listener.stop_listening()
                break

    def eventReceived(self, event):
        print("TestHandler received event")
        if event is None:
            print("None type event, max wait time hit")
            self.endTest()
            return

        self.receive_event_handler(event)

    def endTest(self):
        self.test_over = True
