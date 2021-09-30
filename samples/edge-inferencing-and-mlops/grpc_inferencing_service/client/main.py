import math
import os
import time
import random
from core.inference_client import InferenceClient


def get_env() -> dict:
    inferencing_host = os.getenv("INFERENCING_HOST", "localhost")
    inferencing_port = os.getenv("INFERENCING_PORT", "50051")

    return {"host": inferencing_host, "port": inferencing_port}


def bijection_to_R(x):
    return math.tan(math.pi*(x - 1/2))


if __name__ == '__main__':
    print("inferencing client up")
    while True:
        print("getting prediction")
        env = get_env()
        client = InferenceClient(**env)

        x1 = random.random()
        x1 = bijection_to_R(x1)
        x2 = random.random()
        x2 = bijection_to_R(x2)

        result = client.send_inference_request(x1, x2)
        print(f'predicted class: {result.prediction};\n')
        time.sleep(5)
