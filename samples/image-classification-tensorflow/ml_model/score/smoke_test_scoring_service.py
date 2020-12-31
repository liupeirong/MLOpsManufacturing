import argparse
import requests
import time
from azureml.core import Workspace
from azureml.core.webservice import AciWebservice
from ml_service.util.env_variables import Env
import secrets
import json
import gzip
import os


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
    from io import BytesIO
    from PIL import Image
    from ml_model.preprocess.preprocess_images import resize_image
    import numpy as np

    parser = argparse.ArgumentParser("smoke_test_scoring_service.py")

    parser.add_argument(
        "--service",
        type=str,
        required=True,
        help="Name of the image to test"
    )
    args = parser.parse_args()

    e = Env()

    url_str = os.environ.get("TEST_IMAGE_URLS")
    class_str = os.environ.get("TEST_IMAGE_CLASSES")
    image_urls = url_str.split(',')
    image_classes = class_str.split(',')
    if len(image_urls) != len(image_classes):
        raise "number of urls is not same as number of classes"

    with open("ml_model/parameters.json") as f:
        pars = json.load(f)
        image_size = pars["preprocessing"]["image_size"]
        size = (image_size["x"], image_size["y"])

    img_array = []
    for url_idx in range(len(image_urls)):
        response = requests.get(image_urls[url_idx])
        img = Image.open(BytesIO(response.content))
        img = np.array(resize_image(img, size))
        img_array.append(img.tolist())

    input_json = json.dumps({"data": img_array})
    compressed = gzip.compress(input_json.encode('utf-8'))
    predictions = call_web_service(e, args.service, compressed)
    predicted_classes = json.loads(predictions)
    assert len(predicted_classes) == len(image_classes)
    for (p, a) in zip(predicted_classes, image_classes):
        print(f"predicted: {p}, actual: {a}")
        assert p == a

    print("Smoke test successful.")


if __name__ == '__main__':
    main()
