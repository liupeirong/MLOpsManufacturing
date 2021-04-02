from os import path, getenv
from pathlib import Path
from ssl import _create_unverified_context
from urllib import request
from builtins import input

from dotenv import load_dotenv
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, QuerySpecification

import json
import constants

load_dotenv()


def read_url(url):
    url = url.replace(path.sep, '/')
    resp = request.urlopen(url, context=_create_unverified_context())
    return resp.read()


class GraphManager:
    def __init__(self):
        self.device_id = getenv(constants.device_id)
        self.device_tag = getenv(constants.device_tag)
        self.tag_value = getenv(constants.tag_value)
        self.module_id = getenv(constants.module_id)
        self.api_version = constants.topology_api_version

        self.registry_manager = IoTHubRegistryManager(getenv(constants.iot_connection_string))

        if self.device_id is None:
            self.device_list = self.get_device_list()

    def get_device_list(self):
        query_string = f"SELECT * FROM devices WHERE tags.{self.device_tag} = '{self.tag_value}'"
        query_spec = QuerySpecification(query=query_string)
        response = self.registry_manager.query_iot_hub(query_spec, None, None)
        return response.items

    def invoke(self, method_name, payload):
        if method_name == 'GraphTopologySet':
            self.graph_topology_set(payload)
            return

        if method_name == 'WaitForInput':
            print(payload['message'])
            input()
            return

        self.invoke_module_method(method_name, payload)

    def invoke_module_method(self, method_name, payload):
        # make sure '@apiVersion' has been set
        payload['@apiVersion'] = self.api_version

        module_method = CloudToDeviceMethod(
            method_name=method_name,
            payload=payload,
            response_timeout_in_seconds=30)

        device_id = self.device_id
        try:
            if device_id is None:
                for device in self.device_list:
                    device_id = device.device_id
                    self.invoke_device_module_method(device_id, method_name, module_method, payload)
            else:
                self.invoke_device_module_method(device_id, method_name, module_method, payload)

        except Exception as ex:
            if ex.response.status_code == 404:
                print(">>>>>>>>>> Warning: device '%s' does not have the '%s' module deployed, or the module has not yet initalized <<<<<<<<<<" %
                      (device_id, self.module_id))

    def invoke_device_module_method(self, device_id, method_name, module_method, payload):
        print("\n----------------------- Device: %s - Request: %s  --------------------------------------------------\n" % (device_id, method_name))
        print(json.dumps(payload, indent=4))

        resp = self.registry_manager.invoke_device_module_method(device_id, self.module_id, module_method)

        print("\n----------------------- Device: %s - Response: %s - Status: %s  ------------------------------------\n" %
              (device_id, method_name, resp.status))

        if resp.payload is not None:
            print(json.dumps(resp.payload, indent=4))

    def graph_topology_set(self, op_parameters):
        if op_parameters is None:
            raise Exception('Operation parameters missing')

        if op_parameters.get('topologyUrl') is not None:
            topology_json = read_url(op_parameters['topologyUrl'])
        elif op_parameters.get('topologyFile') is not None:
            topology_path = Path(__file__).parent.joinpath(op_parameters['topologyFile'])
            topology_json = topology_path.read_text()
        else:
            raise Exception('Neither topologyUrl nor topologyFile is specified')

        topology = json.loads(topology_json)

        self.invoke_module_method('GraphTopologySet', topology)


if __name__ == '__main__':
    manager = GraphManager()

    operations_data_json = Path(getenv(constants.operations_file)).read_text()
    operations_data = json.loads(operations_data_json)

    for operation in operations_data['operations']:
        manager.invoke(operation['opName'], operation['opParams'])
