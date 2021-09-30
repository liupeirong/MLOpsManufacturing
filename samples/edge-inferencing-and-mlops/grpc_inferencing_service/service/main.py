import grpc
import os
import pickle

from concurrent import futures
from core.inference_service import InferenceService

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection

from protos import inference_pb2
from protos import inference_pb2_grpc

_LISTEN_HOST = "[::]"
_MODEL_PATH = "./lib/classifier.pkl"
_THREAD_POOL_SIZE = 4


def load_model():
    if not os.path.exists(_MODEL_PATH):
        return None
    clf = pickle.load(open(_MODEL_PATH, 'rb'))
    return clf


def _configure_health_server(server: grpc.Server, port: int) -> None:
    # Add the health servicer to the server.
    listen_address = f"{_LISTEN_HOST}:{port}"
    server.add_insecure_port(listen_address)

    # Create a health check servicer. We use the non-blocking implementation to avoid thread starvation.
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=_THREAD_POOL_SIZE)
    )

    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # Create a tuple of all of the services we want to export via reflection.
    services = tuple(
        service.full_name
        for service in inference_pb2.DESCRIPTOR.services_by_name.values()) + (
            reflection.SERVICE_NAME, health.SERVICE_NAME)

    # Mark all services as healthy.
    for service in services:
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)

    reflection.enable_server_reflection(services, server)


def _configure_inferencing_server(server: grpc.Server, port: int) -> None:
    # Add the application servicer to the server.
    inference_pb2_grpc.add_InferenceServicer_to_server(InferenceService(load_model()), server)
    listen_address = f"{_LISTEN_HOST}:{port}"
    server.add_insecure_port(listen_address)


def serve(inferencing_port: int, health_port: int):
    inferencing_server = grpc.server(futures.ThreadPoolExecutor(max_workers=_THREAD_POOL_SIZE))
    _configure_inferencing_server(inferencing_server, inferencing_port)
    inferencing_server.start()
    print(f"Inferencing server listening on port {inferencing_port}")

    health_server = grpc.server(futures.ThreadPoolExecutor(max_workers=_THREAD_POOL_SIZE))
    _configure_health_server(health_server, health_port)
    health_server.start()
    print(f"Health server listening on port {health_port}")

    inferencing_server.wait_for_termination()
    health_server.wait_for_termination()


if __name__ == "__main__":
    inferencing_port = os.getenv("INFERENCING_PORT", "50051")
    health_port = os.getenv("INFERENCING_PORT", "50039")
    serve(inferencing_port, health_port)
