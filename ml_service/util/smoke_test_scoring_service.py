import argparse
import requests
import time
from azureml.core import Workspace
from azureml.core.webservice import AciWebservice
from ml_service.util.env_variables import Env
import secrets
import json
import gzip


def call_web_service(e, service_name, body):
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    print("Fetching service")
    headers = {'content-encoding': 'gzip'}
    service = AciWebservice(aml_workspace, service_name)
    if service.auth_enabled:
        service_keys = service.get_keys()
        headers['Authorization'] = 'Bearer ' + service_keys[0]
    print("Testing service")
    print(". url: %s" % service.scoring_uri)
    output = call_web_app(service.scoring_uri, headers, body)

    return output


def call_web_app(url, headers, body):

    # Generate an HTTP 'traceparent' distributed tracing header
    # (per the W3C Trace Context proposed specification).
    headers['traceparent'] = "00-{0}-{1}-00".format(
        secrets.token_hex(16), secrets.token_hex(8))

    retries = 30
    for i in range(retries):
        try:
            response = requests.post(
                url, data=body, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if i == retries - 1:
                raise e
            print(e)
            print("Retrying...")
            time.sleep(10)


def main():

    parser = argparse.ArgumentParser("smoke_test_scoring_service.py")

    parser.add_argument(
        "--service",
        type=str,
        required=True,
        help="Name of the image to test"
    )
    args = parser.parse_args()

    with open('./data/smoke-test-data.json') as f:
        input_data = json.load(f)
        compressed_input = gzip.compress(
            json.dumps(input_data).encode('utf-8'))
    expected_output = ['axes']

    e = Env()
    output_json = call_web_service(e, args.service, compressed_input)
    output = json.loads(output_json)
    print("Verifying service output")

    assert expected_output[0] in output
    assert len(expected_output) == len(output)
    print("Smoke test successful.")


if __name__ == '__main__':
    main()
